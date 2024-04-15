from django.db import models

from django_hierarchical_models.models import HierarchicalModel


class PersonModel(HierarchicalModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def hi(self):
        return True
