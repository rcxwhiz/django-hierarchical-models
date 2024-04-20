from django.db import models
from django.db.models import F, Max, QuerySet

from django_hierarchical_models.models.hierarchical_model import HierarchicalModel, T


class NestedSetModel(HierarchicalModel):
    """Nested Set Model implementation of HierarchicalModel.

    Class description here.

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
        skin_chunk = self._manager.filter(_left__lt=self._left, _right__gt=self._right)
        children_chunk = self._manager.filter(
            _left__gt=self._left, _right__lt=self._right
        )
        to_right_chunk = self._manager.filter(_left__gt=self._right)

        self._shift_chunk(skin_chunk, 0, -2)
        self._shift_chunk(children_chunk, -1, -1)
        self._shift_chunk(to_right_chunk, -2, -2)

        super().delete(using=using, keep_parents=keep_parents)

    # ------------------------ override HierarchicalModel ------------------- #

    def parent(self: T) -> T | None:
        self.refresh_from_db(fields=("_left", "_right"))
        return (
            self._manager.filter(_left__lt=self._left, _right__gt=self._right)
            .order_by("-_left")
            .first()
        )

    def is_child_of(self: T, parent: T) -> bool:
        self.refresh_from_db(fields=("_left",))
        parent.refresh_from_db(fields=("_left", "_right"))
        return parent._left < self._left < parent._right

    def _set_parent(self: T, parent: T | None):
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

    def direct_children(self: T) -> QuerySet[T]:
        self.refresh_from_db(fields=("_left", "_right"))
        children_chunk = self._manager.filter(
            _left__gt=self._left, _right__lt=self._right
        ).order_by("_left")
        direct_children = []
        while children_chunk.exists():
            next_child = children_chunk.first()
            direct_children.append(next_child.pk)
            children_chunk = children_chunk.filter(_left__gt=next_child._right)
        return self._manager.filter(pk__in=direct_children)

    def root(self: T) -> T:
        self.refresh_from_db(fields=("_left", "_right"))
        parents_query = self._manager.filter(
            _left__lt=self._left, _right__gt=self._right
        )
        if not parents_query.exists():
            return self
        return parents_query.order_by("_left").first()

    # ------------------------ public class methods ------------------------- #

    def num_children(self) -> int:
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
