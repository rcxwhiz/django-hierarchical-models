from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    """Structured representation of an instance's children.

    Attributes:
        instance: The HierarchicalModel instance for this node.
        children: An ordered list of Nodes for the children of this instance.
    """

    instance: T
    children: list[Node[T]] = field(default_factory=list)

    def __copy__(self):
        return Node(self.instance, [copy.copy(child) for child in self.children])

    def _child_printer(self, s, indent=0, dash=False):
        s[0] += f"\n{' ' * indent}{'- ' if dash else ''}{self.instance}"
        for child in self.children:
            child._child_printer(s, indent + 2, True)

    def __str__(self):
        s = [""]
        self._child_printer(s)
        return s[0]
