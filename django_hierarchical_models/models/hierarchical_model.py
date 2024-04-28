from collections import deque
from collections.abc import Callable
from typing import TypeVar

from django.db import models
from django.db.models import QuerySet
from django.db.models.manager import BaseManager

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
        return self._parent  # type: ignore

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
            root = root._parent  # type: ignore
        return root

    def ancestors(
        self: T,
        max_level: int | None = None,
    ) -> list[T]:
        if max_level is None:
            max_level = -1
        ancestors = []
        ancestor: T | None
        ancestor = self._parent  # type: ignore
        while ancestor is not None and max_level != 0:
            ancestors.append(ancestor)
            ancestor = ancestor._parent  # type: ignore
            max_level -= 1
        return ancestors

    def direct_children(
        self: T,
        object_manager: BaseManager[T] | None = None,
    ) -> QuerySet[T]:
        if object_manager is None:
            object_manager = self.__class__._default_manager
        return object_manager.filter(_parent=self)

    def children(
        self: T,
        max_generations: int | None = None,
        max_siblings: int | None = None,
        max_total: int | None = None,
        sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None = None,
    ) -> Node[T]:
        if max_total is None:
            max_total = -1
        root = Node[T](self)
        queue: deque[tuple[Node[T], Node[T], int]]
        queue = deque([(Node[T](None), root, 0)])  # type: ignore
        while queue and max_total != 0:
            parent, node, generation = queue.popleft()
            parent.children.append(node)
            max_total -= 1
            if max_generations is None or generation < max_generations:
                children = node.instance.direct_children()
                if sibling_transform is not None:
                    children = sibling_transform(children)
                if max_siblings is not None:
                    children = children[:max_siblings]
                for child in children:
                    queue.append((node, Node[T](child), generation + 1))
        return root
