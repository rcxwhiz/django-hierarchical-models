from typing import TypeVar

from django_hierarchical_models.models.hierarchical_model_abc import (
    HierarchicalModelABC,
)

T = TypeVar("T", bound=HierarchicalModelABC)


class HierarchicalModelTestInterface:
    model_class: T

    def test_parent(self):
        parent = self.model_class.objects.create(first_name="Jane", last_name="Doe")
        child = self.model_class.objects.create(parent=parent, first_name="John", last_name="Doe")
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_set_parent(self):
        parent = self.model_class.objects.create(first_name="Jane", last_name="Doe")
        child = self.model_class.objects.create(first_name="John", last_name="Doe")
        self.assertIsNone(parent.parent())
        self.assertIsNone(child.parent())
        child.set_parent(parent)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_direct_children(self):
        parent = self.model_class.objects.create(first_name="Jane", last_name="Doe")
        child = self.model_class.objects.create(parent=parent, first_name="John", last_name="Doe")
        self.assertQuerySetEqual(parent.direct_children(), {child})

    def test_create_child(self):
        parent = self.model_class.objects.create(first_name="Jane", last_name="Doe")
        child = parent.create_child(first_name="John", last_name="Doe")
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_ancestors(self):
        parent = self.model_class.objects.create(first_name="Jane", last_name="Doe")
        child = self.model_class.objects.create(parent=parent, first_name="John", last_name="Doe")
        self.assertListEqual(child.ancestors(), [parent])
