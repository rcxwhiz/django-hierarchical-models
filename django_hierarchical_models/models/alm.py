from collections.abc import Callable

from django.db import models
from django.db.models import QuerySet

from .hierarchical_model import HierarchicalModel, T


class AdjacencyListModel(HierarchicalModel):

    _parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        if len(args) == 0 and "parent" in kwargs:
            kwargs["_parent"] = kwargs.pop("parent")
        super().__init__(*args, **kwargs)

    def parent(self: T) -> T | None:
        return self._parent

    def set_parent(self: T, parent: T | None):
        self._parent = parent
        self.save(update_fields=["_parent"])

    def direct_children(
        self: T, transform: Callable[[QuerySet[T]], QuerySet[T]] | None = None
    ) -> QuerySet[T]:
        queryset = self._manager.filter(_parent=self)
        if transform is not None:
            queryset = transform(queryset)
        return queryset
