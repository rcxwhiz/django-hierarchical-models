from typing import TypeVar

from django.db import connection, models
from django.db.models import QuerySet

from django_hierarchical_models.models.interface import HierarchicalModelInterface

T = TypeVar("T", bound="PathEnumerationModel")


class PathEnumerationModel(HierarchicalModelInterface):

    # ------------------------ class members -------------------------------- #

    _ancestors = models.JSONField(default=list)

    # ------------------------ builtin methods ------------------------------ #

    def __new__(cls, *args, **kwargs):
        if (
            not connection.features.supports_json_field
            or not connection.features.supports_json_field_contains
        ):
            raise NotImplementedError(
                f"This database configuration is missing required JSONField features"
                f"for PathEnumerationModel. SQLite and Oracle do not support these"
                f"features (your vendor: {connection.vendor})."
            )

        # This check only needs to be ran once
        cls.__new__ = lambda a, *b, **c: super().__new__(a)
        return super().__new__(cls)

    def __init__(self, *args, **kwargs):
        if len(args) == 0 and "parent" in kwargs:
            parent = kwargs.pop("parent")
            ancestors = parent._ancestors.copy()
            ancestors.insert(0, parent.pk)
            kwargs["_ancestors"] = ancestors
        super().__init__(*args, **kwargs)

    # ------------------------ override models.Model ------------------------ #

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        children = self._manager.filter(_ancestors__contains=self.pk)
        for child in children:
            child._ancestors = child._ancestors[: child._ancestors.index(self.pk)]
            child.save(update_fields=("_ancestors",))
        super().delete(using=using, keep_parents=keep_parents)

    # ------------------------ override HierarchicalModel ------------------- #

    def parent(self: T) -> T | None:
        self.refresh_from_db(fields=("_ancestors",))
        if len(self._ancestors) == 0:
            return None
        return self._manager.get(pk=self._ancestors[0])

    def is_child_of(self: T, parent: T) -> bool:
        self.refresh_from_db(fields=("_ancestors",))
        return parent.pk in self._ancestors

    def direct_children(self: T) -> QuerySet[T]:
        return self._manager.filter(_ancestors__0=self.pk)

    def root(self: T) -> T:
        self.refresh_from_db(fields=("_ancestors",))
        if len(self._ancestors) == 0:
            return self
        return self._manager.get(pk=self._ancestors[-1])

    def _set_parent(self: T, parent: T | None):
        if parent is None:
            self._ancestors = []
        else:
            parent.refresh_from_db(fields=("_ancestors",))
            self._ancestors = [parent.pk] + parent._ancestors
        self.save(update_fields=("_ancestors",))
