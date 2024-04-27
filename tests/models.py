from django.db import models

from django_hierarchical_models.models import HierarchicalModel


class ExampleModel(HierarchicalModel):
    num = models.IntegerField()

    def __str__(self):
        return str(self.num)
