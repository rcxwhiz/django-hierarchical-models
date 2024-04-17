from typing import TypeVar

from django.test import TestCase

from django_hierarchical_models.models.hierarchical_model import HierarchicalModel
from tests.models import TestModelMixin


class TestHierarchicalModel(TestModelMixin, HierarchicalModel):
    pass


T = TypeVar("T", bound=TestHierarchicalModel)


class HierarchicalModelTestCase(TestCase):
    model_class: T

    def create(self, num: int, **kwargs) -> T:
        return self.model_class.objects.create(num=num, **kwargs)

    def test_basic_parent(self):
        parent = self.create(1)
        child = self.create(2, parent=parent)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_basic_set_parent(self):
        parent = self.create(1)
        child = self.create(2)
        self.assertIsNone(parent.parent())
        self.assertIsNone(child.parent())
        child.num = 3
        child.set_parent(parent)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)
        self.assertEqual(child.num, 3)
        child.refresh_from_db()
        self.assertEqual(child.num, 2)

    def test_basic_direct_children(self):
        parent = self.create(1)
        child = self.create(2, parent=parent)
        self.assertQuerySetEqual(parent.direct_children(), {child})

    def test_basic_create_child(self):
        parent = self.create(1)
        child = parent.create_child(num=2)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_basic_remove_child(self):
        parent = self.create(1)
        child = self.create(2, parent=parent)
        parent.remove_child(child)
        self.assertIsNone(child.parent())

    def test_basic_ancestors(self):
        parent = self.create(1)
        child = self.create(2, parent=parent)
        self.assertListEqual(child.ancestors(), [parent])
