from collections.abc import Callable

# from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F, Max, QuerySet

from django_hierarchical_models.models.hierarchical_model import HierarchicalModel, T


class NestedSetModel(HierarchicalModel):

    _left = models.PositiveIntegerField()
    _right = models.PositiveIntegerField()
    # _depth = models.IntegerField()

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

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        if len(args) == 0:
            if "parent" in kwargs:
                parent = kwargs.pop("parent")
                kwargs["_left"] = parent._right
                kwargs["_right"] = parent._right + 1
                right_of_parent = self.__class__._default_manager.filter(
                    _left__gt=parent._right
                )
                self._shift_chunk(right_of_parent, 2, 2)
                parent._right += 2
                parent.save(update_fields=["_right"])
            else:
                right_most_value = self.__class__._default_manager.aggregate(
                    Max("_right")
                )[
                    "_right__max"
                ]  # TODO could also calculate this
                # based on number of objects, which could be quicker
                if right_most_value is None:
                    right_most_value = -1
                kwargs["_left"] = right_most_value + 1
                kwargs["_right"] = right_most_value + 2
        super().__init__(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        root = self.root()
        if root == self:
            children_chunk = self.__class__._default_manager.filter(
                _left__gt=self._left, _right__lt=self._right
            )
            to_right_chunk = self.__class__._default_manager.filter(
                _left__gt=self._right
            )
            self._shift_chunk(children_chunk, -1, -1)
            self._shift_chunk(to_right_chunk, -2, -2)
        else:
            # TODO not dealing with deleting when a child yet
            pass

    def parent(self: T) -> T | None:
        self.refresh_from_db(fields=("_left", "_right"))
        return (
            self.__class__._default_manager.filter(
                _left__lt=self._left, _right__gt=self._right
            )
            .order_by("-_left")
            .first()
        )

    def set_parent(self: T, parent: T | None):
        if parent == self.parent():
            # left and right were updated by the call to parent()
            return

        self_chunk_size = self._right - self._left + 1
        self_chunk = self.__class__._default_manager.filter(
            _left__gte=self._left, _right__lte=self._right
        )

        if parent is None:
            root = self.root()
            # detect which side is closer
            dist_to_left = self._left - root._left
            dist_to_right = root._right - self._right
            # get out onto that side
            if dist_to_left < dist_to_right:
                old_left = self._left
                self._shift_chunk(self_chunk, -dist_to_left, -dist_to_left)

                fully_between_chunk = self.__class__._default_manager.filter(
                    _left__gt=root._left, _right__lt=old_left
                )
                self._shift_chunk(fully_between_chunk, self_chunk_size, self_chunk_size)

                skin_chunk = self.__class__._default_manager.filter(
                    _left__gte=root._left, _left__lt=old_left, _right__gt=old_left
                )
                self._shift_chunk(skin_chunk, self_chunk_size, 0)
            else:
                old_right = self._right
                self._shift_chunk(self_chunk, dist_to_right, dist_to_right)

                fully_between_chunk = self.__class__._default_manager.filter(
                    _left__gt=old_right, _right__lt=root._right
                )
                self._shift_chunk(
                    fully_between_chunk, -self_chunk_size, -self_chunk_size
                )

                skin_chunk = self.__class__._default_manager.filter(
                    _right__gt=old_right, _right__lte=root._right, _left__lt=old_right
                )
                self._shift_chunk(skin_chunk, 0, -self_chunk_size)

        elif self._left > parent._right:
            # on the right of the parent
            old_left = self._left  # TODO do I even need this?
            # I'm not refreshing from the database. I guess it's more intuitive

            self._shift_chunk(
                self_chunk, -(self._left - parent._right), -(self._left - parent._right)
            )

            between_chunk = self.__class__._default_manager.filter(
                _left__gt=parent._left, _right__lt=old_left
            )
            self._shift_chunk(between_chunk, self_chunk_size, self_chunk_size)

            skin_chunk = self.__class__._default_manager.filter(
                _right__lt=old_left, _right__gte=parent._right, _left__lt=parent._right
            )
            self._shift_chunk(skin_chunk, 0, self_chunk_size)
        elif self._right < parent._left:
            # on the left of the parent
            old_right = self._right

            self._shift_chunk(
                self_chunk, parent._left - self._right, parent._left - self._right
            )

            between_chunk = self.__class__._default_manager.filter(
                _left__gt=old_right, _right__lt=parent._right
            )
            self._shift_chunk(between_chunk, -self_chunk_size, -self_chunk_size)

            skin_chunk = self.__class__._default_manager.filter(
                _left__gt=old_right, _left__lte=parent._left, _right__gt=parent._left
            )
            self._shift_chunk(skin_chunk, -self_chunk_size, 0)
        else:
            # a grandchild of the parent
            # detect closer side
            dist_to_left = self._left - parent._left
            dist_to_right = parent._right - self._right
            if dist_to_left < dist_to_right:
                old_left = self._left
                self._shift_chunk(self_chunk, -dist_to_left + 1, -dist_to_left + 1)

                between_chunks = self.__class__._default_manager.filter(
                    _left__gt=parent._left, _right__lt=old_left
                )
                self._shift_chunk(between_chunks, self_chunk_size, self_chunk_size)

                skin_chunks = self.__class__._default_manager.filter(
                    _left__gt=parent._left, _left__lt=old_left, _right__gt=old_left
                )
                self._shift_chunk(skin_chunks, self_chunk_size, 0)
            else:
                old_right = self._left
                self._shift_chunk(self_chunk, dist_to_right - 1, dist_to_right - 1)

                between_chunks = self.__class__._default_manager.filter(
                    _right__lt=parent._right, _left__gt=old_right
                )
                self._shift_chunk(between_chunks, -self_chunk_size, -self_chunk_size)

                skin_chunks = self.__class__._default_manager.filter(
                    _right__lt=parent._right, _right__gt=old_right, _left__lt=old_right
                )
                self._shift_chunk(skin_chunks, 0, -self_chunk_size)

    def direct_children(
        self: T, transform: Callable[[QuerySet[T]], QuerySet[T]] | None = None
    ) -> QuerySet[T]:
        self.refresh_from_db(fields=("_left", "_right"))
        children_chunk = self.__class__._default_manager.filter(
            _left__gt=self._left, _right__lt=self._right
        ).order_by("_left")
        direct_children = []
        while children_chunk.exists():
            next_child = children_chunk.first()
            direct_children.append(next_child)
            children_chunk = children_chunk.filter(_left__gt=next_child._right)
        direct_children_queryset = self.__class__._default_manager.in_bulk(
            child.pk for child in direct_children
        )
        if transform is not None:
            direct_children_queryset = transform(direct_children_queryset)
        return direct_children_queryset

    def root(self: T) -> T:
        self.refresh_from_db(fields=("_left", "_right"))
        parents_query = self.__class__._default_manager.filter(
            _left__lt=self._left, _right__gt=self._right
        )
        if not parents_query.exists():
            return self
        return parents_query.order_by("_left").first()
