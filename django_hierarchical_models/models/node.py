from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    instance: T
    children: list[Node[T]] = field(default_factory=list)

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
