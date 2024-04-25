from typing import TypeVar

from django.db import models
from django.db.models import F, Max, QuerySet

from django_hierarchical_models.models.interface import HierarchicalModelInterface

T = TypeVar("T", bound="NestedSetModel")


class NestedSetModel(HierarchicalModelInterface):
    """Nested Set Model implementation of HierarchicalModel.

    Each model has two integer fields, a left and a right. In NSM, if a model's
    left value is lower than another, and it's right value is higher, the
    second model is encapsulated by the first, and it is a child.

    This implementation is very efficient for querying, but not so efficient
    for editing. It is possible for every single left and right value in the
    database to be decremented by one operation. This is countered by the
    excellent query performance of this model.

    Attributes:
        _left: holds the left bound for this instance.
        _right: holds the right bound for this instance.
    """

    # ------------------------ class members -------------------------------- #

    _left = models.PositiveIntegerField()
    _right = models.PositiveIntegerField()

    # ------------------------ builtin methods ------------------------------ #

    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            if "parent" in kwargs:
                parent = kwargs.pop("parent")
                parent.refresh_from_db(fields=("_left", "_right"))
                kwargs["_left"] = parent._right
                kwargs["_right"] = parent._right + 1
                right_of_parent = self._manager.filter(_left__gt=parent._right)
                self._shift_chunk(right_of_parent, 2, 2)
                parent._right += 2
                parent.save(update_fields=["_right"])
            else:
                right_most_value = self._manager.aggregate(Max("_right"))["_right__max"]
                if right_most_value is None:
                    right_most_value = -1
                kwargs["_left"] = right_most_value + 1
                kwargs["_right"] = right_most_value + 2
        super().__init__(*args, **kwargs)

    # ------------------------ override models.Model ------------------------ #

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Necessary to "free up" space."""
        root = self.root()
        dist_to_root = root._right - self._left
        children_space = self._right - self._left - 1

        parents_chunk = self._manager.filter(
            _left__lt=self._left, _right__gt=self._right
        )
        num_parents = len(parents_chunk)

        siblings_chunk = self._manager.filter(
            _left__gt=self._right, _right__lt=root._right
        )
        to_right_chunk = self._manager.filter(_left__gt=self._right)
        children = (
            child.pk
            for child in self._manager.filter(
                _left__gt=self._left, _right__lt=self._right
            )
        )

        self._shift_chunk(siblings_chunk, -2 - children_space, -2 - children_space)
        self._shift_chunk(parents_chunk, 0, -2 - children_space)
        self._shift_chunk(to_right_chunk, -2, -2)

        children_chunk = self._manager.filter(pk__in=children)
        self._shift_chunk(
            children_chunk,
            dist_to_root - num_parents - 1 - children_space,
            dist_to_root - num_parents - 1 - children_space,
        )

        super().delete(using=using, keep_parents=keep_parents)

    # ------------------------ override HierarchicalModel ------------------- #

    def parent(self: T) -> T | None:
        """The parent of the AdjacencyModel instance.

        Triggers a partial refresh_from_db()

        Queries for models with lower _left and higher _right values, then
        returns the one with the highest _left value, meaning the one closest
        to this instance.

        Returns:
            Parent instance, or None if there is no parent.
        """

        self.refresh_from_db(fields=("_left", "_right"))
        return (
            self._manager.filter(_left__lt=self._left, _right__gt=self._right)
            .order_by("-_left")
            .first()
        )

    def is_child_of(self: T, parent: T) -> bool:
        """Checks if the instance is at any level a child to the parent.

        The only test to do where is whether the parent's _left and _right are
        smaller and larger than the values of this instance.
        """

        self.refresh_from_db(fields=("_left",))
        parent.refresh_from_db(fields=("_left", "_right"))
        return parent._left < self._left < parent._right

    def _set_parent(self: T, parent: T | None):
        """Assigns the given model as the parent.

        This method tries to find the direction to shift models that will result
        in the least database updates. After that, it is a matter of which
        models are having their _left and _right members shifted by how much.

        Due to the trouble that cycles pose to these data structures, a check
        is made if the parent is already a child to this model in any way.

        Some models in which it is possible to represent a cycle have a
        .set_parent_unchecked() method which will skip this step. That method
        should be used with great care since it can be extremely difficult to
        repair models that have cycles.

        Raises:
            CycleException: A cycle would be formed by this operation - skipped.
        """
        if parent == self.parent():
            # left and right were updated by the call to parent()
            return

        if parent is not None:
            parent.refresh_from_db(fields=("_left", "_right"))

        self_chunk_size = self._right - self._left + 1
        self_chunk_items = (
            item.pk
            for item in self._manager.filter(
                _left__gte=self._left, _right__lte=self._right
            )
        )

        self_shift: tuple[int, int]
        between_shift: tuple[QuerySet[T], int, int]
        skin_shift: tuple[QuerySet[T], int, int]

        if parent is None:
            # need to be orphaned
            root = self.root()
            dist_to_left = self._left - root._left
            dist_to_right = root._right - self._right
            if dist_to_left < dist_to_right:
                self_shift = -dist_to_left, -dist_to_left
                between_shift = (
                    self._manager.filter(_left__gt=root._left, _right__lt=self._left),
                    self_chunk_size,
                    self_chunk_size,
                )
                skin_shift = (
                    self._manager.filter(
                        _left__gte=root._left,
                        _left__lt=self._left,
                        _right__gt=self._left,
                    ),
                    self_chunk_size,
                    0,
                )
            else:
                self_shift = dist_to_right, dist_to_right
                between_shift = (
                    self._manager.filter(_left__gt=self._right, _right__lt=root._right),
                    -self_chunk_size,
                    -self_chunk_size,
                )
                skin_shift = (
                    self._manager.filter(
                        _right__gt=self._right,
                        _right__lte=root._right,
                        _left__lt=self._right,
                    ),
                    0,
                    -self_chunk_size,
                )
        elif self._left > parent._right:
            # on the right of the parent
            self_shift = -(self._left - parent._right), -(self._left - parent._right)
            between_shift = (
                self._manager.filter(_left__gt=parent._right, _right__lt=self._left),
                self_chunk_size,
                self_chunk_size,
            )
            skin_shift = (
                self._manager.filter(
                    _right__lt=self._left,
                    _right__gte=parent._right,
                    _left__lt=parent._right,
                ),
                0,
                self_chunk_size,
            )
        elif self._right < parent._left:
            # on the left of the parent
            self_shift = parent._left - self._right, parent._left - self._right
            between_shift = (
                self._manager.filter(_left__gt=self._right, _right__lt=parent._left),
                -self_chunk_size,
                -self_chunk_size,
            )
            skin_shift = (
                self._manager.filter(
                    _left__gt=self._right,
                    _left__lte=parent._left,
                    _right__gt=parent._left,
                ),
                -self_chunk_size,
                0,
            )
        else:
            # already grandchild of parent
            dist_to_left = self._left - parent._left
            dist_to_right = parent._right - self._right
            if dist_to_left < dist_to_right:
                self_shift = -dist_to_left + 1, -dist_to_left + 1
                between_shift = (
                    self._manager.filter(_left__gt=parent._left, _right__lt=self._left),
                    self_chunk_size,
                    self_chunk_size,
                )
                skin_shift = (
                    self._manager.filter(
                        _left__gt=parent._left,
                        _left__lt=self._left,
                        _right__gt=self._left,
                    ),
                    self_chunk_size,
                    0,
                )
            else:
                self_shift = dist_to_right - 1, dist_to_right - 1
                between_shift = (
                    self._manager.filter(
                        _right__lt=parent._right, _left__gt=self._right
                    ),
                    -self_chunk_size,
                    -self_chunk_size,
                )
                skin_shift = (
                    self._manager.filter(
                        _right__lt=parent._right,
                        _right__gt=self._right,
                        _left__lt=self._right,
                    ),
                    0,
                    -self_chunk_size,
                )

        self._shift_chunk(*between_shift)
        self._shift_chunk(*skin_shift)
        self_chunk = self._manager.filter(pk__in=self_chunk_items)
        self._shift_chunk(self_chunk, *self_shift)

    def ancestors(self: T, max_level: int | None = None) -> list[T]:
        self.refresh_from_db(fields=("_left", "_right"))
        ancestors = self._manager.filter(
            _left__lt=self._left, _right__gt=self._right
        ).order_by("-_left")
        if max_level is not None:
            ancestors = ancestors[:max_level]
        return list(ancestors)

    def direct_children(self: T) -> QuerySet[T]:
        """Gets all the direct descendants of a model.

        If there are no children the QuerySet will be emtpy.

        This method first queries for models that are within the bounds of this
        instance. After that they are ordered by smallest and the first is
        selected. The next child *after* the _right value of that child is
        chosen. This skips the grandchildren contained in those children.

        Returns:
            An unordered QuerySet of all direct children of this model.
        """
        self.refresh_from_db(fields=("_left", "_right"))
        children_chunk = self._manager.filter(
            _left__gt=self._left, _right__lt=self._right
        ).order_by("_left")
        direct_children = []

        right_value = -1
        for child in children_chunk:
            if child._left > right_value:
                direct_children.append(child.pk)
                right_value = child._right
        return self._manager.filter(pk__in=direct_children)

    def root(self: T) -> T:
        self.refresh_from_db(fields=("_left", "_right"))
        parents_query = self._manager.filter(
            _left__lt=self._left, _right__gt=self._right
        )
        root = parents_query.order_by("_left").first()
        return root if root is not None else self

    # ------------------------ public class methods ------------------------- #

    def num_children(self) -> int:
        self.refresh_from_db(fields=("_left", "_right"))
        return (self._right - self._left) // 2

    # ------------------------ private class methods ------------------------ #

    def _shift_chunk(self: T, chunk: QuerySet[T], left_shift: int, right_shift: int):
        if left_shift != 0:
            if right_shift != 0:
                chunk.update(
                    _left=F("_left") + left_shift, _right=F("_right") + right_shift
                )
            else:
                chunk.update(_left=F("_left") + left_shift)
        elif right_shift != 0:
            chunk.update(_right=F("_right") + right_shift)
