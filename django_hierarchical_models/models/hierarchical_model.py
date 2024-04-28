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
    """An abstract Django model supporting hierarchical data."""

    _parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )

    def __init__(self, *args, **kwargs):
        """Initialize with an optional "parent" kwarg.

        Keyword Args:
            parent: Parent model of this instance.
        """
        if len(args) == 0 and "parent" in kwargs:
            kwargs["_parent"] = kwargs.pop("parent")
        super().__init__(*args, **kwargs)

    class Meta:
        abstract = True

    def parent(self: T) -> T | None:
        """The parent of this instance.

        Returns:
            The instance of the parent, or None if this instance has no parent.
        """
        return self._parent  # type: ignore

    def set_parent(self: T, parent: T | None, unchecked: bool = False):
        """Set the parent of this instance.

        Args:
            parent: The new parent of this instance, or None to make this
              instance an orphan.
            unchecked: If true, there will be no check for cycles. Default
              False.

        Raises:
            CycleException: This operation would create a cycle.
        """

        if (
            not unchecked
            and parent is not None
            and (parent == self or parent.is_child_of(self))
        ):
            raise CycleException(parent, self)
        self._parent = parent
        self.save(update_fields=("_parent",))

    def is_child_of(self: T, parent: T) -> bool:
        """Checks if this instance is a child of parent.

        Args:
            parent: Potential parent instance.

        Returns:
            True if the instance is a child of parent at any level. Returns
            false when checked against itself.
        """

        ancestor = self._parent
        while ancestor is not None:
            if ancestor == parent:
                return True
            ancestor = ancestor._parent
        return False

    def root(self: T) -> T:
        """Root of this instance.

        Returns:
            The top level root of this instance. Will return self if an orphan.
        """

        root = self
        while root._parent is not None:
            root = root._parent  # type: ignore
        return root

    def ancestors(
        self: T,
        max_level: int | None = None,
    ) -> list[T]:
        """Ancestors of this instance.

        Args:
            max_level: Optional maximum number of ancestors.

        Returns:
            An ordered list of ancestors instances, with the closest ancestor
            at the lowest index of the list.
        """

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
        """The direct children of this instance.

        Args:
            object_manager: An optional object manager to use to query. Uses
              model's default object manager when none is provided.

        Returns:
            An unordered QuerySet containing all the direct children of this
            instance.
        """

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
        """Get all children of this instance.

        Returns all children of this instance (or set limited by optional
        parameters), structured as instances of Node.

        Args:
            max_generations: Optional maximum number of generations to find,
              eg. 1 would only find direct children.
            max_siblings: Optional maximum number of siblings to take from each
              instance.
            max_total: Optional maximum total number of instances to find.
            sibling_transform: A callable applied to each sibling query. This
              will affect the order the children will appear in each returned
              node. It is applied before the number of siblings is limited, if
              applicable, so it will also determine which siblings are taken.

        Returns:
            An instance of Node, containing a reference to this instance, and
            an ordered list of Nodes for the children taken for this instance.
        """

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
