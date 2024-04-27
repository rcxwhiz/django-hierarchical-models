from typing import TypeVar

from django.db import models
from django.db.models import Manager, QuerySet

from django_hierarchical_models.models.exceptions import CycleException
from django_hierarchical_models.models.node import Node

T = TypeVar("T", bound="HierarchicalModel")


class HierarchicalModel(models.Model):

    _parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __init__(self, *args, **kwargs):
        if len(args) == 0 and "parent" in kwargs:
            kwargs["_parent"] = kwargs.pop("parent")
        super().__init__(*args, **kwargs)

    class Meta:
        abstract = True

    def parent(self: T) -> T | None:
        return self._parent

    def set_parent(self: T, parent: T | None, unchecked: bool = False):
        if (
            not unchecked
            and parent is not None
            and (parent == self or parent.is_child_of(self))
        ):
            raise CycleException(parent, self)
        self._parent = parent
        self.save(update_fields=("_parent",))

    def is_child_of(self: T, parent: T) -> bool:
        ancestor = self._parent
        while ancestor is not None:
            if ancestor == parent:
                return True
            ancestor = ancestor._parent
        return False

    def root(self: T) -> T:
        root = self
        while root._parent is not None:
            root = root._parent
        return root

    def ancestors(
        self: T,
        max_level: int | None = None,
    ) -> list[T]:  # TODO more generic type hint? also this can be cleaned up
        if max_level is None:
            max_level = -1
        ancestors = []
        ancestor = self._parent
        while ancestor is not None and max_level != 0:
            ancestors.append(ancestor)
            ancestor = ancestor._parent
            max_level -= 1
        return ancestors

    def direct_children(
        self: T,
        object_manager: Manager[T] | None = None,
    ) -> QuerySet[T]:
        if object_manager is None:
            object_manager = self.__class__._default_manager
        return object_manager.filter(_parent=self)

    def children(self: T) -> Node[T]:
        raise NotImplementedError()
