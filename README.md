# django-hierarchical-models

[![Tests](https://github.com/rcxwhiz/django-hierarchical-models/actions/workflows/test.yml/badge.svg)](https://github.com/rcxwhiz/django-hierarchical-models/actions/workflows/)
[![Coverage](https://codecov.io/gh/rcxwhiz/django-hierarchical-models/branch/main/graph/badge.svg)](https://codecov.io/gh/rcxwhiz/django-hierarchical-models/)
[![PyPi](https://img.shields.io/pypi/v/django-hierarchical-models.svg)](https://pypi.python.org/pypi/django-hierarchical-models/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/django-hierarchical-models.svg)](https://pypi.python.org/pypi/django-hierarchical-models/)
[![Supported Django versions](https://img.shields.io/pypi/djversions/django-hierarchical-models.svg)](https://pypi.python.org/pypi/django-hierarchical-models/)

This package provides several implementations Django models which support hierarchical
data. Efficiently modeling hierarchical, or tree like data, in a relational database
can be non-trivial. The following models implement the same interface, but there have
different tradeoffs.

`models.HierarchicalModelInterface`

This abstract model defines the shared functionality of all hierarchical models. Some
models may implement additional methods which are cheap for their implementation.

`models.AdjacencyListModel`

This is the most trivial implementation, using a single `_parent` foreign key field.
Edits are efficient in this model, but queries for children/parents can be very
expensive.

`models.PathEnumerationModel`

This model uses a `_ancestors` json field to store the path to its root. This model
has middle ground efficiency for edits and queries. **NOTE:** This model requires
database features that are not available in Oracle or SQLite backends. An exception
will be raised if you attempt to use this model with an unsupported backend.

`models.NestedSetModel`

This model uses `_left` and `_right` integer fields to determine which instances it is
parent/child to. Queries can be very efficient in this model, but edits can be very
expensive, possibly even requiring updates to `_left` and `_right` fields of ever model
instance for a single edit.

`models.Node`

Calls to `HierarchicalModel.children()` return this type, which has `instance` and
`children` members, with the children being additional instances of `Node`.
