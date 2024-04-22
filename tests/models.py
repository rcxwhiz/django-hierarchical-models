from django.db import models

from django_hierarchical_models.models import (
    AdjacencyListModel,
    NestedSetModel,
    PathEnumerationModel,
)


class NumberModelMixin(models.Model):
    num = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.num)


class ALMTestModel(NumberModelMixin, AdjacencyListModel):
    pass


class NSMTestModel(NumberModelMixin, NestedSetModel):
    def __str__(self):
        return f"({self.num}|{self._left}|{self._right})"


class PEMTestModel(NumberModelMixin, PathEnumerationModel):
    pass
