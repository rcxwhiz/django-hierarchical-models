from itertools import pairwise

from django.test import TestCase

from django_hierarchical_models.models import HierarchicalModelInterface
from tests.models import ALMTestModel, NSMTestModel, PEMTestModel


class EditBenchmark(TestCase):
    model_class = HierarchicalModelInterface

    def setUp(self):
        self.instances = [self.model_class.objects.create(num=i) for i in range(1000)]

    def test_create_large(self):
        for i in range(5000):
            self.model_class.objects.create(num=i)

    def test_create_child(self):
        for i, instance in enumerate(self.instances):
            instance.create_child(num=i + len(self.instances))

    def test_set_parents(self):
        for child, parent in pairwise(self.instances):
            child.set_parent(parent)
        for parent, child in pairwise(self.instances[::-1]):
            child.set_parent(parent)
        for instance in self.instances:
            instance.set_parent(None)

        for i in range(len(self.instances) // 2):
            child, parent = (
                self.instances[i],
                self.instances[i + len(self.instances) // 2],
            )
            child.set_parent(parent)

    def test_delete(self):
        for instance in self.instances[::2]:
            instance.delete()

        for instance in self.instances[1::2]:
            instance.delete()

    def test_delete_parents(self):
        for i in range(len(self.instances) // 2):
            child, parent = self.instances[i], self.instances[-i - 1]
            child.set_parent(parent)

        for instance in self.instances[::2]:
            instance.delete()

        for instance in self.instances[1::2]:
            instance.delete()

    def test_add_child(self):
        for instance in self.instances[:-1]:
            self.instances[-1].add_child(instance)

    def test_remove_child(self):
        for instance in self.instances[:-1]:
            self.instances[-1].add_child(instance)

        for instance in self.instances[:-1]:
            self.instances[-1].remove_child(instance)


class ALMEditBenchmark(EditBenchmark):
    model_class = ALMTestModel

    def test_set_parents_unchecked(self):
        for child, parent in pairwise(self.instances):
            child.set_parent_unchecked(parent)
        for parent, child in pairwise(self.instances[::-1]):
            child.set_parent_unchecked(parent)
        for instance in self.instances:
            instance.set_parent_unchecked(None)

        for i in range(len(self.instances) // 2):
            child, parent = (
                self.instances[i],
                self.instances[i + len(self.instances) // 2],
            )
            child.set_parent_unchecked(parent)


class NSMEditBenchmark(EditBenchmark):
    model_class = NSMTestModel


class PEMEditBenchmark(EditBenchmark):
    model_class = PEMTestModel


class QueryBenchmark(TestCase):
    model_class = HierarchicalModelInterface
    n: int
    density: int

    @classmethod
    def setUpTestData(cls):
        cls.instances = []
        for i in range(cls.n):
            if i % cls.density == 0:
                cls.instances.append(cls.model_class.objects.create(num=i))
            else:
                cls.instances.append(
                    cls.instances[(i * 31) % len(cls.instances)].create_child(num=i)
                )

    def test_get_parent(self):
        for instance in self.instances:
            _ = instance.parent()

    def test_get_ancestors(self):
        for instance in self.instances:
            _ = instance.ancestors()

    def test_get_direct_children(self):
        for instance in self.instances:
            _ = instance.direct_children()

    def test_get_children(self):
        for instance in self.instances:
            _ = instance.children()

    def test_get_root(self):
        for instance in self.instances:
            _ = instance.root()

    def test_is_child_of(self):
        for instance_1, instance_2 in pairwise(self.instances):
            _ = instance_1.is_child_of(instance_2)
            _ = instance_2.is_child_of(instance_1)


class ALMQueryBenchmark(QueryBenchmark):
    model_class = ALMTestModel
    n = 50000
    density = 10


class NSMQueryBenchmark(QueryBenchmark):
    model_class = NSMTestModel
    n = 1000
    density = 3


class PEMQueryBenchmark(QueryBenchmark):
    model_class = PEMTestModel
    n = 50000
    density = 10
