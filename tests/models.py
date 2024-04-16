from django.db import models

from django_hierarchical_models.models import AdjacencyListModel


class PersonModelMixin(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        abstract = True


class ALMPerson(PersonModelMixin, AdjacencyListModel):
    pass
