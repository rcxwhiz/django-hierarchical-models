# django-hierarchical-models

[![Tests](https://github.com/rcxwhiz/django-hierarchical-models/actions/workflows/test.yml/badge.svg)](https://github.com/rcxwhiz/django-hierarchical-models/actions/workflows/)
[![Coverage](https://codecov.io/gh/rcxwhiz/django-hierarchical-models/branch/main/graph/badge.svg)](https://codecov.io/gh/rcxwhiz/django-hierarchical-models/)
[![PyPi](https://img.shields.io/pypi/v/django-hierarchical-models.svg)](https://pypi.python.org/pypi/django-hierarchical-models/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/django-hierarchical-models.svg)](https://pypi.python.org/pypi/django-hierarchical-models/)
[![Supported Django versions](https://img.shields.io/pypi/djversions/django-hierarchical-models.svg)](https://pypi.python.org/pypi/django-hierarchical-models/)

This package provides an abstract Django model which supports hierarchical data. The
implementation is an adjacency list, which is rather naive, but actually has higher
performance in this scenario than other implementations such as path enumeration or
nested sets because those implementations store more data with each instance which must
be updated before almost every operation, effectively doubling (or more) database
queries and killing performance. The performance of this implementation actually holds
up pretty well at large numbers of instances.

## Usage

```python
from django.db import models
from django_hierarchical_models.models import HierarchicalModel

class MyModel(HierarchicalModel):
    name = models.CharField(max_length=100)

...

child = MyModel.objects.create(name="Betty")
child.parent  # None

parent = MyModel.objects.create(name="Simon")
# checks for pesky cycles
child.set_parent(parent)
# alternative
# child.parent = parent
child.parent  # <MyModel: "Simon">

child.root()  # <MyModel: "Simon">
parent.root()  # <MyModel: "Simon">

parent.direct_children()  # [<MyModel: "Betty">]

child.is_child_of(parent)  # True
parent.is_child_of(child)  # False
```

## parent = vs .set_parent()

`parent` is a `ForeignKeyField` which may be directly accessed or set. The
`.set_parent()` method checks to see if the operation would create a cycle, which can
be bad for some of the other instance methods. The `.set_parent()` method is slower
because it must determine if a cycle would be formed. `.set_parent()` makes a call to
`.save(update_fields=("parent",))`, so it is not necessary to call `.save()` after
updating the parent this way.

## Refreshing from database

The following is expected behavior:

```python
instance_1 = MyModel.objects.create(name="Betty")
instance_2 = MyModel.objects.create(parent=instance_1, name="Simon")
instance_2.parent  # <MyModel: "Betty">

instance_1.delete()

instance_2.parent  # <MyModel: "Betty">

instance_2.refresh_from_db()

instance_2.parent  # None
```

```python
instance_1 = MyModel.objects.create(name="Betty")
instance_2 = MyModel.objects.create(parent=instance_1, name="Simon")
instance_3 = MyModel.objects.create(parent=instance_2, name="Finn")
instance_3_copy = MyModel.objects.get(pk=instance_3.pk)

instance_1.root()  # <MyModel: "Betty">
instance_2.root()  # <MyModel: "Betty">
instance_3.root()  # <MyModel: "Betty">
instance_3_copy.root()  # <MyModel: "Betty">

instance_2.set_parent(None)

instance_1.root()  # <MyModel: "Betty">
instance_2.root()  # <MyModel: "Simon">
instance_3.root()  # <MyModel: "Simon">
instance_3_copy.root()  # <MyModel: "Betty">

instance_3_copy.refresh_from_db()

instance_1.root()  # <MyModel: "Betty">
instance_2.root()  # <MyModel: "Simon">
instance_3.root()  # <MyModel: "Simon">
instance_3_copy.root()  # <MyModel: "Simon">
```

Moral of the story, if your instance's parent might have been edited/deleted, you will
want to refresh your instance for that change to be reflected.  

## Benchmarks

The following benchmarks demonstrate that the query performance of the model stays the
same from 10,000 to 1,000,000 models. These tests were done with Postgres. The results
are in the form `total time (s) / per instance (ms)`. Eventually the query performance
of this model should scale down with the total number of instances in the database,
but it appears up to these scales those effects are insignificant compared to other
overhead.

| n         | Chance Child | Query Parent  | Query Root    | Is Child Of   | Query Ancestors | Query Direct Children | Query Children |
|-----------|--------------|---------------|---------------|---------------|-----------------|-----------------------|----------------|
| 10,000    | 50%          | 0.29 / 0.029  | 0.27 / 0.027  | 0.27 / 0.027  | 0.29 / 0.029    | 0.78 / 0.078          | 3.85 / 0.385   |
| 10,000    | 90%          | 0.30 / 0.030  | 0.39 / 0.039  | 0.31 / 0.031  | 0.30 / 0.030    | 0.87 / 0.087          | 5.07 / 0.507   |
| 100,000   | 50%          | 3.46 / 0.035  | 3.12 / 0.031  | 3.55 / 0.036  | 3.09 / 0.031    | 8.24 / 0.082          | 37.89 / 0.380  |
| 100,000   | 90%          | 4.10 / 0.041  | 3.48 / 0.035  | 3.88 / 0.039  | 3.55 / 0.036    | 8.89 / 0.089          | 48.30 / 0.483  |
| 1,000,000 | 50%          | 32.39 / 0.032 | 34.53 / 0.035 | 35.41 / 0.035 | 32.16 / 0.032   | 86.05 / 0.086         | 385.62 / 0.386 |
| 1,000,000 | 90%          | 34.87 / 0.035 | 38.59 / 0.039 | 38.93 / 0.039 | 36.51 / 0.037   | 87.49 / 0.087         | 490.65 / 0.491 |
