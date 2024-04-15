from abc import ABCMeta, abstractmethod
from typing import TypeVar

from django.db import models

T = TypeVar("T")


class HierarchicalModelABCMeta(ABCMeta, type(models.Model)):
    pass


class HierarchicalModelABC(models.Model, metaclass=HierarchicalModelABCMeta):
    @abstractmethod
    def parent(self: T) -> T | None:
        pass
