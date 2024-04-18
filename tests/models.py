from django.db import models

from django_hierarchical_models.models import AdjacencyListModel, NestedSetModel


class TestModelMixin(models.Model):
    num = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.num)


class ALMTestModel(TestModelMixin, AdjacencyListModel):
    pass


class NSMTestModel(TestModelMixin, NestedSetModel):
    def __str__(self):
        return f"({self.num}|{self._left}|{self._right})"
