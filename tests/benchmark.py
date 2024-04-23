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

    def setUp(self):
        num_layers = 4
        num_siblings = 5
        layer = [self.model_class.objects.create(num=i) for i in range(num_siblings)]
        for _ in range(num_layers):
            new_layer = []
            for instance in layer:
                for _ in range(num_siblings):
                    new_layer.append(instance.create_child(num=0))
            layer = new_layer
        self.instances = list(self.model_class.objects.all())

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


class ALMQueryBenchmark(QueryBenchmark):
    model_class = ALMTestModel


class NSMQueryBenchmark(QueryBenchmark):
    model_class = NSMTestModel


class PEMQueryBenchmark(QueryBenchmark):
    model_class = PEMTestModel
