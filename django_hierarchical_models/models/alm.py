from typing import TypeVar

from django.db import models
from django.db.models import QuerySet

from django_hierarchical_models.models.interface import HierarchicalModelInterface

T = TypeVar("T", bound="AdjacencyListModel")


class AdjacencyListModel(HierarchicalModelInterface):
    """Adjacency List Model implementation of HierarchicalModel.

    Class description here.

    """

    # ------------------------ class members -------------------------------- #

    _parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )

    # ------------------------ builtin methods ------------------------------ #

    def __init__(self, *args, **kwargs):
        if len(args) == 0 and "parent" in kwargs:
            kwargs["_parent"] = kwargs.pop("parent")
        super().__init__(*args, **kwargs)

    # ------------------------ override models.Model ------------------------ #

    class Meta:
        abstract = True

    # ------------------------ override HierarchicalModel ------------------- #

    def parent(self: T) -> T | None:
        self.refresh_from_db(fields=("_parent",))
        return self._parent  # type: ignore

    def is_child_of(self: T, parent: T) -> bool:
        self_parent = self._parent
        while self_parent is not None:
            if self_parent == parent:
                return True
            self_parent = self_parent._parent
        return False

    def _set_parent(self: T, parent: T | None):
        self._parent = parent
        self.save(update_fields=["_parent"])

    def set_parent_unchecked(self: T, parent: T | None):
        """Sets the parent of this instance without checking for cycles."""
        self._set_parent(parent)

    def direct_children(self: T) -> QuerySet[T]:
        return self._manager.filter(_parent=self)

    def root(self: T) -> T:
        root = self
        self.refresh_from_db(fields=("_parent",))
        while root._parent is not None:
            root = root._parent  # type: ignore
        return root
