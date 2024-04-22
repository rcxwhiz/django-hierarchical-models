import pytest
from django.test import TestCase

from tests.interface_tester import HierarchicalModelInterfaceTester
from tests.models import ALMTestModel, NSMTestModel, PEMTestModel


class ALMInterfaceTest(HierarchicalModelInterfaceTester, TestCase):
    model_class = ALMTestModel


class NSMInterfaceTest(HierarchicalModelInterfaceTester, TestCase):
    model_class = NSMTestModel


@pytest.mark.skip("Needs non-sqlite")
class PEMInterfaceTest(HierarchicalModelInterfaceTester, TestCase):
    model_class = PEMTestModel
