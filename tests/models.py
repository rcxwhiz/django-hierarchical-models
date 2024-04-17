from django.db import models

from django_hierarchical_models.models import AdjacencyListModel


class TestModelMixin(models.Model):
    num = models.IntegerField()

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.num)


class ALMTestModel(TestModelMixin, AdjacencyListModel):
    pass
