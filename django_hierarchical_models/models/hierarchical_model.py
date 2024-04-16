from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections import deque
from collections.abc import Callable
from typing import TypeVar

from django.db import models
from django.db.models import QuerySet

from django_hierarchical_models.models.exceptions import (
    AlreadyHasParentException,
    NotAChildException,
)

T = TypeVar("T", bound="HierarchicalModel")


class HierarchicalModelABCMeta(ABCMeta, type(models.Model)):
    pass


class HierarchicalModel(models.Model, metaclass=HierarchicalModelABCMeta):

    class Node:
        def __init__(
            self, instance: T, children: list[HierarchicalModel.Node] | None = None
        ):
            self.instance = instance
            self.children = children

    @abstractmethod
    def parent(self: T) -> T | None:
        pass

    @abstractmethod
    def set_parent(self: T, parent: T | None):
        pass

    @abstractmethod
    def direct_children(self: T) -> QuerySet[T]:
        pass

    @abstractmethod
    def create_child(
        self: T, create_method: Callable[..., T] | None = None, **kwargs
    ) -> T:
        pass

    def add_child(self: T, child: T):
        if child.parent() is not None:
            raise AlreadyHasParentException(child)
        child.set_parent(self)

    def remove_child(self: T, child: T):
        if child.parent() is not self:
            raise NotAChildException(self, child)
        child.set_parent(None)

    def ancestors(self: T, max_level: int | None = None) -> list[T]:
        if self.parent() is None or (max_level is not None and max_level <= 0):
            return []
        if max_level is not None:
            max_level -= 1
        return self.parent().ancestors(max_level=max_level) + [self.parent()]

    def children(
        self: T,
        max_generations: int | None = None,
        max_siblings: int | None = None,
        max_total: int | None = None,
    ) -> HierarchicalModel.Node:
        root = HierarchicalModel.Node(self)
        if (
            (max_generations is not None and max_generations < 1)
            or (max_siblings is not None and max_siblings < 1)
            or (max_total is not None and max_total < 2)
        ):
            return root
        self._child_finder(root, max_generations, max_siblings, max_total)
        return root

    def _child_finder(
        self,
        root: HierarchicalModel.Node,
        max_generations: int | None,
        max_siblings: int | None,
        max_total: int | None,
    ):
        f = _dispatch_table[
            (
                max_generations is not None,
                max_siblings is not None,
                max_total is not None,
            )
        ]
        f(root, max_generations, max_siblings, max_total)


def _no_no_no(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
):
    queue = deque([(HierarchicalModel.Node(None), root)])
    while queue:
        parent_node, node = queue.popleft()
        parent_node.children.append(node)
        for child in node.instance.direct_children():
            child_node = HierarchicalModel.Node(child)
            queue.append((node, child_node))


def _yes_no_no(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
):
    queue = deque([(HierarchicalModel.Node(None), root, 0)])
    while queue:
        parent_node, node, generation = queue.popleft()
        parent_node.children.append(node)
        if generation < max_generations:
            for child in node.instance.direct_children():
                child_node = HierarchicalModel.Node(child)
                queue.append((node, child_node, generation + 1))


def _no_yes_no(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
):
    queue = deque([(HierarchicalModel.Node(None), root)])
    while queue:
        parent_node, node = queue.popleft()
        parent_node.children.append(node)
        for child in node.instance.direct_children()[:max_siblings]:
            child_node = HierarchicalModel.Node(child)
            queue.append((node, child_node))


def _no_no_yes(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
):
    queue = deque([(HierarchicalModel.Node(None), root)])
    max_total -= 1
    while queue:
        parent_node, node = queue.popleft()
        parent_node.children.append(node)
        for child in node.instance.direct_children()[:max_total]:
            child_node = HierarchicalModel.Node(child)
            queue.append((node, child_node))
            max_total -= 1


def _yes_yes_no(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
):
    queue = deque([(HierarchicalModel.Node(None), root, 0)])
    while queue:
        parent_node, node, generation = queue.popleft()
        parent_node.children.append(node)
        if generation < max_generations:
            for child in node.instance.direct_children()[:max_siblings]:
                child_node = HierarchicalModel.Node(child)
                queue.append((node, child_node, generation + 1))


def _yes_no_yes(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
):
    queue = deque([(HierarchicalModel.Node(None), root, 0)])
    max_total -= 1
    while queue:
        parent_node, node, generation = queue.popleft()
        parent_node.children.append(node)
        if generation < max_generations:
            for child in node.instance.direct_children()[:max_total]:
                child_node = HierarchicalModel.Node(child)
                queue.append((node, child_node, generation + 1))
                max_total -= 1


def _no_yes_yes(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
):
    queue = deque([(HierarchicalModel.Node(None), root)])
    max_total -= 1
    while queue:
        parent_node, node = queue.popleft()
        parent_node.children.append(node)
        num_siblings = min(max_siblings, max_total)
        for child in node.instance.direct_children()[:num_siblings]:
            child_node = HierarchicalModel.Node(child)
            queue.append((node, child_node))
            max_total -= 1


def _yes_yes_yes(
    root: HierarchicalModel.Node,
    max_generations: int,
    max_siblings: int,
    max_total: int,
):
    queue = deque([(HierarchicalModel.Node(None), root, 0)])
    max_total -= 1
    while queue:
        parent_node, node, generation = queue.popleft()
        parent_node.children.append(node)
        if generation < max_generations:
            num_siblings = min(max_siblings, max_total)
            for child in node.instance.direct_children()[:num_siblings]:
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
