from django.db import models

from .hierarchical_model_abc import HierarchicalModelABC, T


class AdjacencyListModel(HierarchicalModelABC):

    _parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        abstract = True

    def parent(self: T) -> T | None:
        return self._parent
