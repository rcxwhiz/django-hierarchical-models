from django.db import models

from django_hierarchical_models.models import AdjacencyListModel


class ALMPerson(AdjacencyListModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
