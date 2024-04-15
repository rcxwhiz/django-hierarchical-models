from django.db import models


class AdjacencyListModel(models.Model):

    test_field = models.IntegerField()

    class Meta:
        abstract = True
