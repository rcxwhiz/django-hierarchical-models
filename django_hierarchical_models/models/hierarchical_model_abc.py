from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from typing import TypeVar

from django.db import models
from django.db.models import QuerySet

T = TypeVar("T")


class HierarchicalModelABCMeta(ABCMeta, type(models.Model)):
    pass


class HierarchicalModelABC(models.Model, metaclass=HierarchicalModelABCMeta):
    @abstractmethod
    def parent(self: T) -> T | None:
        pass

    @abstractmethod
    def set_parent(self: T, parent: T):
        pass

    @abstractmethod
    def direct_children(self: T) -> QuerySet[T]:
        pass

    @abstractmethod
    def create_child(self: T, create_method: Callable[..., T] | None = None, **kwargs) -> T:
        pass

    @abstractmethod
    def ancestors(self: T, max_level: int | None = None) -> list[T]:
        pass

    # TODO need to figure out how to structure children return
