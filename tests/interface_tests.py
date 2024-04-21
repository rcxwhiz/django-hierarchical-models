from tests.hierarchical_model_test import HierarchicalModelInterfaceTest
from tests.models import ALMTestModel, NSMTestModel, PETestModel


class ALMInterfaceTest(HierarchicalModelInterfaceTest):
    model_class = ALMTestModel


class NSMInterfaceTest(HierarchicalModelInterfaceTest):
    model_class = NSMTestModel


class PEInterfaceTest(HierarchicalModelInterfaceTest):
    model_class = PETestModel
