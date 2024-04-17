from collections.abc import Callable

# from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import F, Max, QuerySet

from django_hierarchical_models.models.hierarchical_model import HierarchicalModel, T


class NestedSetModel(HierarchicalModel):

    _left = models.PositiveIntegerField()
    _right = models.PositiveIntegerField()
    # _depth = models.IntegerField()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        if "parent" in kwargs:
            parent_right = kwargs["parent"]._right
            kwargs["_left"] = parent_right
            kwargs["_right"] = parent_right + 1
            self.__class__._default_manager.filter(_right_gte=parent_right).update(
                _right=F("_right") + 2
            )
        else:
            right_most_value = self.__class__._default_manager.aggregate(Max("_right"))[
                "_right__max"
            ]
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
            children_chunk.update(_left=F("_left") - 1, _right=F("_right") - 1)
            to_right_chunk.update(_left=F("_left") - 2, _right=F("_right") - 2)
        else:
            # TODO not dealing with deleting when a child yet
            pass

    def parent(self: T) -> T | None:
        parents_query = self.__class__._default_manager.filter(
            _left__lt=self._left, _right__gt=self._right
        )
        if not parents_query.exists():
            return None
        return parents_query.order_by("-_left").first()

    def set_parent(self: T, parent: T | None):
        if parent == self.parent():
            return

        self_chunk_size = self._right - self._left
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
                fully_between_chunk = self.__class__._default_manager.filter(
                    _left__gt=root._left, _right__lt=self._left
                )
                skin_chunk = self.__class__._default_manager.filter(
                    _left__gt=root._left, _left__lt=self._left, _right__gt=self._right
                )

                self_chunk.update(
                    _left=F("_left") - dist_to_left, _right=F("_right") - dist_to_left
                )
                fully_between_chunk.update(
                    _left=F("_left") + self_chunk_size,
                    _right=F("_right") + self_chunk_size,
                )
                skin_chunk.update(_left=F("_left") + self_chunk_size)
                root._left += self_chunk_size
                root.save(update_fields=["_left"])
            else:
                fully_between_chunk = self.__class__._default_manager.filter(
                    _left__gt=self._right, _right__lt=root._right
                )
                skin_chunk = self.__class__._default_manager.filter(
                    _right__gt=self._right, _right__lt=root._right, _left__lt=self._left
                )

                self_chunk.update(
                    _left=F("_left") + dist_to_right, _right=F("_right") + dist_to_right
                )
                fully_between_chunk.update(
                    _left=F("_left") - self_chunk_size,
                    _right=F("_right") - self_chunk_size,
                )
                skin_chunk.update(_right=F("_right") - self_chunk_size)
                root._right -= self_chunk_size
                root.save(update_fields=["_right"])

        elif self._left > parent._right:
            # on the right of the parent
            between_chunk_size = self._left - parent._right
            between_chunk = self.__class__._default_manager.filter(
                _left__gt=parent._left, _right__lt=self._left
            )

            self_chunk.update(
                _left=F("_left") - between_chunk_size,
                _right=F("_right") - between_chunk_size,
            )
            between_chunk.update(
                _left=F("_left") + self_chunk_size, _right=F("_right") + self_chunk_size
            )

            parent._right += self._right - self._left
            parent.save(update_fields=["_right"])
        elif self._right < parent._left:
            # on the left of the parent
            between_chunk_size = parent._left - self._right
            between_chunk = self.__class__._default_manager.filter(
                _left__gt=parent._left, _right__lt=self._left
            )

            self_chunk.update(
                _left=F("_left") + between_chunk_size,
                _right=F("_right") + between_chunk_size,
            )
            between_chunk.update(
                _left=F("_left") - self_chunk_size, _right=F("_right") - self_chunk_size
            )

            parent._left -= self._right - self._left
            parent.save(update_fields=["_left"])
        else:
            # a grandchild of the parent
            # detect closer side
            dist_to_left = self._left - parent._left
            dist_to_right = parent._right - self._right
            if dist_to_left < dist_to_right:
                fully_between_chunk = self.__class__._default_manager.filter(
                    _left__gt=parent._left, _right__lt=self._right
                )
                skin_chunk = self.__class__._default_manager.filter(
                    _left__gt=parent._left, _left__lt=self._left, _right__gt=self._right
                )

                self_chunk.update(
                    _left=F("_left") - dist_to_left, _right=F("_right") - dist_to_left
                )
                fully_between_chunk.update(
                    _left=F("_left") + self_chunk_size,
                    _right=F("_right") + self_chunk_size,
                )
                skin_chunk.update(_left=F("_left") + self_chunk_size)
            else:
                fully_between_chunk = self.__class__._default_manager.filter(
                    _left__gt=self._right, _right__lt=parent._right
                )
                skin_chunk = self.__class__._default_manager.filter(
                    _right__gt=self._right,
                    _right__lt=parent._right,
                    _left__lt=self._left,
                )

                self_chunk.update(
                    _left=F("_left") + dist_to_right, _right=F("_right") + dist_to_right
                )
                fully_between_chunk.update(
                    _left=F("_left") - self_chunk_size,
                    _right=F("_right") - self_chunk_size,
                )
                skin_chunk.update(_left=F("_left") - self_chunk_size)

    def direct_children(
        self: T, transform: Callable[[QuerySet[T]], QuerySet[T]] | None = None
    ) -> QuerySet[T]:
        children_chunk = self.__class__._default_manager.filter(
            _left__gt=self._left, _right__lt=self._right
        ).order_by("_left")
        direct_children = []
        while children_chunk.exists():
            next_child = children_chunk.first()
            direct_children.append(next_child)
            children_chunk = children_chunk.filter(_left__gt=next_child._right)
        return self.__class__._default_manager.in_bulk(
            child.pk for child in direct_children
        )

    def root(self: T) -> T:
        parents_query = self.__class__._default_manager.filter(
            _left__lt=self._left, _right__gt=self._right
        )
        if not parents_query.exists():
            return self
        return parents_query.order_by("_left").first()
