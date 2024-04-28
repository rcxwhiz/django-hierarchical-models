from itertools import pairwise

from django.test import TestCase

from tests.models import ExampleModel


class QueryBenchmark(TestCase):
    n: int
    density: int

    @classmethod
    def setUpTestData(cls):
        cls.instances = []
        for i in range(cls.n):
            if i % cls.density == 0:
                cls.instances.append(ExampleModel.objects.create(num=i))
            else:
                cls.instances.append(
                    ExampleModel.objects.create(
                        num=i, parent=cls.instances[(i * 31) % len(cls.instances)]
                    )
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


class ATest(QueryBenchmark):
    n = 10000
    density = 2


class BTest(QueryBenchmark):
    n = 10000
    density = 10


class CTest(QueryBenchmark):
    n = 100000
    density = 2


class DTest(QueryBenchmark):
    n = 100000
    density = 10


class ETest(QueryBenchmark):
    n = 1000000
    density = 2


class FTest(QueryBenchmark):
    n = 1000000
    density = 10
