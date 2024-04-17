from tests.hierarchical_model_test import HierarchicalModelTestCase
from tests.models import ALMTestModel, NSMTestModel


class AdjacencyListModelTests(HierarchicalModelTestCase):
    model_class = ALMTestModel


class NestedSetModelTests(HierarchicalModelTestCase):
    model_class = NSMTestModel
