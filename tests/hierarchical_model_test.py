from typing import TypeVar

from django.test import TestCase

from django_hierarchical_models.models.hierarchical_model import HierarchicalModel
from tests.models import PersonModelMixin


class TestHierarchicalModel(PersonModelMixin, HierarchicalModel):
    pass


T = TypeVar("T", bound=TestHierarchicalModel)


class HierarchicalModelTestCase(TestCase):
    model_class: T

    def create(self, **kwargs) -> T:
        return self.model_class.objects.create(**kwargs)

    def test_basic_parent(self):
        parent = self.create()
        child = self.create(parent=parent)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_basic_set_parent(self):
        parent = self.create()
        child = self.create(first_name="A", last_name="B")
        self.assertIsNone(parent.parent())
        self.assertIsNone(child.parent())
        child.first_name = "C"
        child.last_name = "D"
        child.set_parent(parent)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)
        self.assertEqual(child.first_name, "C")
        self.assertEqual(child.last_name, "D")
        child.refresh_from_db()
        self.assertEqual(child.first_name, "A")
        self.assertEqual(child.last_name, "B")

    def test_basic_direct_children(self):
        parent = self.create()
        child = self.create(parent=parent)
        self.assertQuerySetEqual(parent.direct_children(), {child})

    def test_basic_create_child(self):
        parent = self.create()
        child = parent.create_child()
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_basic_remove_child(self):
        parent = self.create()
        child = self.create(parent=parent)
        parent.remove_child(child)
        self.assertIsNone(child.parent())

    def test_basic_ancestors(self):
        parent = self.create()
        child = self.create(parent=parent)
        self.assertListEqual(child.ancestors(), [parent])
