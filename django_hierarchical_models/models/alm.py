from typing import override

from django.db import models
from django.db.models import QuerySet

from .hierarchical_model import HierarchicalModel, T


class AdjacencyListModel(HierarchicalModel):
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

    @override
    def parent(self: T) -> T | None:
        self.refresh_from_db(fields=("_parent",))
        return self._parent

    @override
    def is_child_of(self: T, parent: T) -> bool:
        self.refresh_from_db(fields=("_parent",))
        if self._parent is None:
            return False
        if self._parent == parent:
            return True
        return self._parent.is_child_of(parent)

    @override
    def _set_parent(self: T, parent: T | None):
        self._parent = parent
        self.save(update_fields=["_parent"])

    @override
    def direct_children(self: T) -> QuerySet[T]:
        return self._manager.filter(_parent=self)
