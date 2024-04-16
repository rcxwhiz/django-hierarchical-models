from collections.abc import Callable

from django.db import models
from django.db.models import QuerySet

from .hierarchical_model_abc import HierarchicalModelABC, T


class AdjacencyListModel(HierarchicalModelABC):

    _parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        if "parent" in kwargs:
            kwargs["_parent"] = kwargs.pop("parent")
        super().__init__(*args, **kwargs)

    def parent(self: T) -> T | None:
        return self._parent

    def set_parent(self: T, parent: T):
        self._parent = parent
        self.save()

    def direct_children(self: T) -> QuerySet[T]:
        return self.__class__.objects.filter(_parent=self)

    def create_child(
        self: T, create_method: Callable[..., T] | None = None, **kwargs
    ) -> T:
        if create_method is None:
            create_method = self.__class__.objects.create
        return create_method(_parent=self, **kwargs)

    def ancestors(self: T, max_level: int | None = None) -> list[T]:
        if self._parent is None or (max_level is not None and max_level <= 0):
            return []
        if max_level is not None:
            max_level -= 1
        return self._parent.ancestors(max_level=max_level) + [self._parent]
