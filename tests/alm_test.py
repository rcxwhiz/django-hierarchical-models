from django.test import TestCase

from django_hierarchical_models.models.exceptions import CycleException
from tests.models import ALMTestModel


class ALMTests(TestCase):
    def test_set_parent_unchecked(self):
        n1 = ALMTestModel.objects.create(num=1)
        n2 = n1.create_child(num=2)
        self.assertIsNone(n1.parent())
        self.assertEqual(n2.parent(), n1)
        with self.assertRaises(CycleException) as cm:
            n1.set_parent(n2)
        self.assertEqual(cm.exception.child, n1)
        self.assertEqual(cm.exception.parent, n2)
        self.assertIsNone(n1.parent())
        self.assertEqual(n2.parent(), n1)
        n1.set_parent_unchecked(n2)
        self.assertEqual(n1.parent(), n2)
        self.assertEqual(n2.parent(), n1)
