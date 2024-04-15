from django.test import TestCase

from tests.hm_test_interface import HierarchicalModelTestInterface
from tests.models import ALMPerson


class AdjacencyListModelTests(HierarchicalModelTestInterface, TestCase):
    model_class = ALMPerson
