from django.test import TestCase

from tests.models import NSMTestModel


class NSMTests(TestCase):

    def assert_chunk(self, node: NSMTestModel, left: int, right: int):
        self.assertEqual(node._left, left, f"{node}._left != {left}")
        self.assertEqual(node._right, right, f"{node}._right != {right}")

    def test_child_from_right(self):
        n1 = NSMTestModel.objects.create(num=1)
        self.assert_chunk(n1, 0, 1)
        n2 = NSMTestModel.objects.create(num=2)
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 3)
        n3 = NSMTestModel.objects.create(num=3)
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 3)
        self.assert_chunk(n3, 4, 5)
        n3.set_parent(n2)
        n1.refresh_from_db()
        n2.refresh_from_db()
        n3.refresh_from_db()
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 5)
        self.assert_chunk(n3, 3, 4)
        n2.set_parent(n1)
        n1.refresh_from_db()
        n2.refresh_from_db()
        n3.refresh_from_db()
        self.assert_chunk(n1, 0, 5)
        self.assert_chunk(n2, 1, 4)
        self.assert_chunk(n3, 2, 3)

    def test_child_from_left(self):
        n1 = NSMTestModel.objects.create(num=1)
        self.assert_chunk(n1, 0, 1)
        n2 = NSMTestModel.objects.create(num=2)
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 3)
        n3 = NSMTestModel.objects.create(num=3)
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 3)
        self.assert_chunk(n3, 4, 5)
        n1.set_parent(n2)
        n1.refresh_from_db()
        n2.refresh_from_db()
        n3.refresh_from_db()
        self.assert_chunk(n1, 1, 2)
        self.assert_chunk(n2, 0, 3)
        self.assert_chunk(n3, 4, 5)
        n2.set_parent(n3)
        n1.refresh_from_db()
        n2.refresh_from_db()
        n3.refresh_from_db()
        self.assert_chunk(n1, 2, 3)
        self.assert_chunk(n2, 1, 4)
        self.assert_chunk(n3, 0, 5)
