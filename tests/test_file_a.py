from django.test import TestCase

from tests.models import PersonModel


class SimpleTests(TestCase):
    def test_simple(self):
        x = PersonModel(first_name="Josh", last_name="B")
        self.assertTrue(x.hi())
