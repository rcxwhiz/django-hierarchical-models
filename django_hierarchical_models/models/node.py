from __future__ import annotations

import copy
from typing import Generic, TypeVar

T = TypeVar("T")


class Node(Generic[T]):
    def __init__(
        self,
        instance: T,
        children: list[Node[T]] | None = None,
    ):
        self.instance = instance
        self.children = children if children is not None else []

    def __eq__(self, other):
        if not isinstance(other, Node):
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
        return Node(self.instance, [copy.copy(child) for child in self.children])

    def _p(self, s, indent=0, dash=False):
        s[0] += f"\n{' ' * indent}{'- ' if dash else ''}{self.instance}"
        for child in self.children:
            child._p(s, indent + 2, True)

    def __str__(self):
        s = [""]
        self._p(s)
        return s[0]
