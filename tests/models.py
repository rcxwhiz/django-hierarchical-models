from django.db import models

from django_hierarchical_models.alm import AdjacencyListModel


class PersonModel(AdjacencyListModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def hi(self):
        return True
