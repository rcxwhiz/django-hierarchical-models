from tests.hierarchical_model_test import HierarchicalModelTestCase
from tests.models import ALMPerson


class AdjacencyListModelTests(HierarchicalModelTestCase):
    model_class = ALMPerson
