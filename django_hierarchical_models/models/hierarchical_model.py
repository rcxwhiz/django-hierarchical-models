from __future__ import annotations

import copy
from abc import ABCMeta, abstractmethod
from collections import deque
from collections.abc import Callable
from typing import TypeVar

from django.db import models
from django.db.models import Manager, QuerySet

from django_hierarchical_models.models.exceptions import (
    AlreadyHasParentException,
    CycleException,
    NotAChildException,
)

T = TypeVar("T", bound="HierarchicalModel")


class HierarchicalModelABCMeta(ABCMeta, type(models.Model)):
    pass


class HierarchicalModel(models.Model, metaclass=HierarchicalModelABCMeta):

    # ------------------------ override models.Model ------------------------ #

    class Meta:
        abstract = True

    # ------------------------ public abstract methods ---------------------- #

    @abstractmethod
    def parent(self: T) -> T | None:
        pass

    @abstractmethod
    def is_child_of(self: T, parent: T) -> bool:
        pass

    @abstractmethod
    def direct_children(
        self: T, transform: Callable[[QuerySet[T]], QuerySet[T]] | None = None
    ) -> QuerySet[T]:
        pass

    # ------------------------ public class methods ------------------------- #

    def set_parent(self: T, parent: T | None):
        if parent is not None and (parent == self or parent.is_child_of(self)):
            raise CycleException(parent, self)
        self._set_parent(parent)

    def create_child(
        self: T, create_method: Callable[..., T] | None = None, **kwargs
    ) -> T:
        if create_method is None:
            create_method = self._manager.create
        return create_method(parent=self, **kwargs)

    def add_child(self: T, child: T, check_has_parent: bool = False):
        if check_has_parent and child.parent() is not None:
            raise AlreadyHasParentException(child)
        child.set_parent(self)

    def remove_child(self: T, child: T, check_is_child: bool = False):
        if child.parent() == self:
            child._set_parent(None)
        elif check_is_child:
            raise NotAChildException(self, child)

    def ancestors(self: T, max_level: int | None = None) -> list[T]:
        if self.parent() is None or (max_level is not None and max_level <= 0):
            return []
        if max_level is not None:
            max_level -= 1
        return [self.parent()] + self.parent().ancestors(max_level=max_level)

    def root(self: T) -> T:
        if self.parent() is None:
            return self
        return self.parent().root()

    def children(
        self: T,
        max_generations: int | None = None,
        max_siblings: int | None = None,
        max_total: int | None = None,
        sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None = None,
    ) -> HierarchicalModel.Node:
        root = HierarchicalModel.Node(self)
        if (
            (max_generations is not None and max_generations < 1)
            or (max_siblings is not None and max_siblings < 1)
            or (max_total is not None and max_total < 2)
        ):
            return root
        self._child_finder(
            root, max_generations, max_siblings, max_total, sibling_transform
        )
        return root

    # ------------------------ private class methods ------------------------ #

    def _child_finder(
        self,
        root: HierarchicalModel.Node,
        max_generations: int | None,
        max_siblings: int | None,
        max_total: int | None,
        sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None,
    ):
        f = _dispatch_table[
            (
                max_generations is not None,
                max_siblings is not None,
                max_total is not None,
            )
        ]
        f(root, max_generations, max_siblings, max_total, sibling_transform)

    @property
    def _manager(self: T) -> Manager[T]:
        return self.__class__._default_manager

    # ------------------------ private abstract methods --------------------- #

    @abstractmethod
    def _set_parent(self: T, parent: T | None):
        pass

    # ------------------------ internal classes ----------------------------- #

    class Node:
        def __init__(
            self, instance: T, children: list[HierarchicalModel.Node] | None = None
        ):
            self.instance = instance
            self.children = children if children is not None else []

        def __eq__(self, other):
            if not isinstance(other, HierarchicalModel.Node):
                return False
            if self.instance != other.instance:
                return False
            if len(self.children) != len(other.children):
                return False
            return all(
                self_child == other_child
                for self_child, other_child in zip(self.children, other.children)
            )

        def __copy__(self):
            return HierarchicalModel.Node(
                self.instance, [copy.copy(child) for child in self.children]
            )

        def _p(self, s, indent=0, dash=False):
            s[0] += f"\n{' ' * indent}{'- ' if dash else ''}{self.instance}"
            for child in self.children:
                child._p(s, indent + 2, True)

        def __str__(self):
            s = [""]
            self._p(s)
            return s[0]


# ------------------------ dispatch functions ------------------------------- #


def _no_no_no(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
    sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None,
):
    queue = deque([(HierarchicalModel.Node(None), root)])
    while queue:
        parent_node, node = queue.popleft()
        parent_node.children.append(node)
        for child in node.instance.direct_children(sibling_transform):
            child_node = HierarchicalModel.Node(child)
            queue.append((node, child_node))


def _yes_no_no(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
    sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None,
):
    queue = deque([(HierarchicalModel.Node(None), root, 0)])
    while queue:
        parent_node, node, generation = queue.popleft()
        parent_node.children.append(node)
        if generation < max_generations:
            for child in node.instance.direct_children(sibling_transform):
                child_node = HierarchicalModel.Node(child)
                queue.append((node, child_node, generation + 1))


def _no_yes_no(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
    sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None,
):
    queue = deque([(HierarchicalModel.Node(None), root)])
    while queue:
        parent_node, node = queue.popleft()
        parent_node.children.append(node)
        for child in node.instance.direct_children(sibling_transform)[:max_siblings]:
            child_node = HierarchicalModel.Node(child)
            queue.append((node, child_node))


def _no_no_yes(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
    sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None,
):
    queue = deque([(HierarchicalModel.Node(None), root)])
    max_total -= 1
    while queue:
        parent_node, node = queue.popleft()
        parent_node.children.append(node)
        for child in node.instance.direct_children(sibling_transform)[:max_total]:
            child_node = HierarchicalModel.Node(child)
            queue.append((node, child_node))
            max_total -= 1


def _yes_yes_no(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
    sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None,
):
    queue = deque([(HierarchicalModel.Node(None), root, 0)])
    while queue:
        parent_node, node, generation = queue.popleft()
        parent_node.children.append(node)
        if generation < max_generations:
            for child in node.instance.direct_children(sibling_transform)[
                :max_siblings
            ]:
                child_node = HierarchicalModel.Node(child)
                queue.append((node, child_node, generation + 1))


def _yes_no_yes(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
    sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None,
):
    queue = deque([(HierarchicalModel.Node(None), root, 0)])
    max_total -= 1
    while queue:
        parent_node, node, generation = queue.popleft()
        parent_node.children.append(node)
        if generation < max_generations:
            for child in node.instance.direct_children(sibling_transform)[:max_total]:
                child_node = HierarchicalModel.Node(child)
                queue.append((node, child_node, generation + 1))
                max_total -= 1


def _no_yes_yes(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
    sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None,
):
    queue = deque([(HierarchicalModel.Node(None), root)])
    max_total -= 1
    while queue:
        parent_node, node = queue.popleft()
        parent_node.children.append(node)
        num_siblings = min(max_siblings, max_total)
        for child in node.instance.direct_children(sibling_transform)[:num_siblings]:
            child_node = HierarchicalModel.Node(child)
            queue.append((node, child_node))
            max_total -= 1


def _yes_yes_yes(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
    sibling_transform: Callable[[QuerySet[T]], QuerySet[T]] | None,
):
    queue = deque([(HierarchicalModel.Node(None), root, 0)])
    max_total -= 1
    while queue:
        parent_node, node, generation = queue.popleft()
        parent_node.children.append(node)
        if generation < max_generations:
            num_siblings = min(max_siblings, max_total)
            for child in node.instance.direct_children(sibling_transform)[
                :num_siblings
            ]:
                child_node = HierarchicalModel.Node(child)
                queue.append((node, child_node, generation + 1))
                max_total -= 1


_dispatch_table = {
    (False, False, False): _no_no_no,
    (True, False, False): _yes_no_no,
    (False, True, False): _no_yes_no,
    (False, False, True): _no_no_yes,
    (True, True, False): _yes_yes_no,
    (True, False, True): _yes_no_yes,
    (False, True, True): _no_yes_yes,
    (True, True, True): _yes_yes_yes,
}
