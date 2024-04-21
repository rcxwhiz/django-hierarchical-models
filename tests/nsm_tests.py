from django.test import TestCase

from tests.models import NSMTestModel


class NSMTests(TestCase):

    def assert_chunk(self, node: NSMTestModel, left: int, right: int):
        self.assertEqual(node._left, left, f"{node}._left != {left}")
        self.assertEqual(node._right, right, f"{node}._right != {right}")

    def test_child_from_right(self):
        n1 = NSMTestModel.objects.create(num=1)
        self.assert_chunk(n1, 0, 1)
        self.assertIsNone(n1.parent())
        self.assertQuerySetEqual(n1.direct_children(), [])
        self.assertEqual(n1.root(), n1)

        self.assertQuerySetEqual(n1.direct_children(), [])
        n2 = NSMTestModel.objects.create(num=2)
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 3)
        self.assertIsNone(n1.parent())
        self.assertIsNone(n2.parent())
        self.assertQuerySetEqual(n1.direct_children(), [])
        self.assertQuerySetEqual(n2.direct_children(), [])
        self.assertEqual(n1.root(), n1)
        self.assertEqual(n2.root(), n2)

        n3 = NSMTestModel.objects.create(num=3)
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 3)
        self.assert_chunk(n3, 4, 5)
        self.assertIsNone(n1.parent())
        self.assertIsNone(n2.parent())
        self.assertIsNone(n3.parent())
        self.assertQuerySetEqual(n1.direct_children(), [])
        self.assertQuerySetEqual(n2.direct_children(), [])
        self.assertQuerySetEqual(n3.direct_children(), [])
        self.assertEqual(n1.root(), n1)
        self.assertEqual(n2.root(), n2)
        self.assertEqual(n3.root(), n3)

        n3.set_parent(n2)
        n1.refresh_from_db()
        n2.refresh_from_db()
        n3.refresh_from_db()
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 5)
        self.assert_chunk(n3, 3, 4)
        self.assertIsNone(n1.parent())
        self.assertIsNone(n2.parent())
        self.assertEqual(n3.parent(), n2)
        self.assertQuerySetEqual(n1.direct_children(), [])
        self.assertQuerySetEqual(n2.direct_children(), [n3])
        self.assertQuerySetEqual(n3.direct_children(), [])
        self.assertEqual(n1.root(), n1)
        self.assertEqual(n2.root(), n2)
        self.assertEqual(n3.root(), n2)

        n2.set_parent(n1)
        n1.refresh_from_db()
        n2.refresh_from_db()
        n3.refresh_from_db()
        self.assert_chunk(n1, 0, 5)
        self.assert_chunk(n2, 1, 4)
        self.assert_chunk(n3, 2, 3)
        self.assertIsNone(n1.parent())
        self.assertEqual(n2.parent(), n1)
        self.assertEqual(n3.parent(), n2)
        self.assertQuerySetEqual(n1.direct_children(), [n2])
        self.assertQuerySetEqual(n2.direct_children(), [n3])
        self.assertQuerySetEqual(n3.direct_children(), [])
        self.assertEqual(n1.root(), n1)
        self.assertEqual(n2.root(), n1)
        self.assertEqual(n3.root(), n1)

    def test_child_from_left(self):
        n1 = NSMTestModel.objects.create(num=1)
        self.assert_chunk(n1, 0, 1)
        self.assertIsNone(n1.parent())
        self.assertQuerySetEqual(n1.direct_children(), [])
        self.assertEqual(n1.root(), n1)

        n2 = NSMTestModel.objects.create(num=2)
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 3)
        self.assertIsNone(n1.parent())
        self.assertIsNone(n2.parent())
        self.assertQuerySetEqual(n1.direct_children(), [])
        self.assertQuerySetEqual(n2.direct_children(), [])
        self.assertEqual(n1.root(), n1)
        self.assertEqual(n2.root(), n2)

        n3 = NSMTestModel.objects.create(num=3)
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 3)
        self.assert_chunk(n3, 4, 5)
        self.assertIsNone(n1.parent())
        self.assertIsNone(n2.parent())
        self.assertIsNone(n3.parent())
        self.assertQuerySetEqual(n1.direct_children(), [])
        self.assertQuerySetEqual(n2.direct_children(), [])
        self.assertQuerySetEqual(n3.direct_children(), [])
        self.assertEqual(n1.root(), n1)
        self.assertEqual(n2.root(), n2)
        self.assertEqual(n3.root(), n3)

        n1.set_parent(n2)
        n1.refresh_from_db()
        n2.refresh_from_db()
        n3.refresh_from_db()
        self.assert_chunk(n1, 1, 2)
        self.assert_chunk(n2, 0, 3)
        self.assert_chunk(n3, 4, 5)
        self.assertEqual(n1.parent(), n2)
        self.assertIsNone(n2.parent())
        self.assertIsNone(n3.parent())
        self.assertQuerySetEqual(n1.direct_children(), [])
        self.assertQuerySetEqual(n2.direct_children(), [n1])
        self.assertQuerySetEqual(n3.direct_children(), [])
        self.assertEqual(n1.root(), n2)
        self.assertEqual(n2.root(), n2)
        self.assertEqual(n3.root(), n3)

        n2.set_parent(n3)
        n1.refresh_from_db()
        n2.refresh_from_db()
        n3.refresh_from_db()
        self.assert_chunk(n1, 2, 3)
        self.assert_chunk(n2, 1, 4)
        self.assert_chunk(n3, 0, 5)
        self.assertEqual(n1.parent(), n2)
        self.assertEqual(n2.parent(), n3)
        self.assertIsNone(n3.parent())
        self.assertQuerySetEqual(n1.direct_children(), [])
        self.assertQuerySetEqual(n2.direct_children(), [n1])
        self.assertQuerySetEqual(n3.direct_children(), [n2])
        self.assertEqual(n1.root(), n3)
        self.assertEqual(n2.root(), n3)
        self.assertEqual(n3.root(), n3)

    def test_consolidate(self):
        n1 = NSMTestModel.objects.create(num=1)
        n2 = NSMTestModel.objects.create(num=2)
        n3 = NSMTestModel.objects.create(num=3)
        n4 = NSMTestModel.objects.create(num=4)
        n5 = NSMTestModel.objects.create(num=5)
        n6 = NSMTestModel.objects.create(num=6)
        n7 = NSMTestModel.objects.create(num=7)
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 3)
        self.assert_chunk(n3, 4, 5)
        self.assert_chunk(n4, 6, 7)
        self.assert_chunk(n5, 8, 9)
        self.assert_chunk(n6, 10, 11)
        self.assert_chunk(n7, 12, 13)
        n7.set_parent(n2)
        for node in (n1, n2, n3, n4, n5, n6, n7):
            node.refresh_from_db()
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 5)
        self.assert_chunk(n3, 6, 7)
        self.assert_chunk(n4, 8, 9)
        self.assert_chunk(n5, 10, 11)
        self.assert_chunk(n6, 12, 13)
        self.assert_chunk(n7, 3, 4)
        n4.set_parent(n5)
        for node in (n1, n2, n3, n4, n5, n6, n7):
            node.refresh_from_db()
        self.assert_chunk(n1, 0, 1)
        self.assert_chunk(n2, 2, 5)
        self.assert_chunk(n3, 6, 7)
        self.assert_chunk(n4, 9, 10)
        self.assert_chunk(n5, 8, 11)
        self.assert_chunk(n6, 12, 13)
        self.assert_chunk(n7, 3, 4)
        n1.set_parent(n5)
        for node in (n1, n2, n3, n4, n5, n6, n7):
            node.refresh_from_db()
        self.assert_chunk(n1, 7, 8)
        self.assert_chunk(n2, 0, 3)
        self.assert_chunk(n3, 4, 5)
        self.assert_chunk(n4, 9, 10)
        self.assert_chunk(n5, 6, 11)
        self.assert_chunk(n6, 12, 13)
        self.assert_chunk(n7, 1, 2)
        n5.set_parent(n2)
        for node in (n1, n2, n3, n4, n5, n6, n7):
            node.refresh_from_db()
        self.assert_chunk(n1, 4, 5)
        self.assert_chunk(n2, 0, 9)
        self.assert_chunk(n3, 10, 11)
        self.assert_chunk(n4, 6, 7)
        self.assert_chunk(n5, 3, 8)
        self.assert_chunk(n6, 12, 13)
        self.assert_chunk(n7, 1, 2)
        n3.set_parent(n1)
        for node in (n1, n2, n3, n4, n5, n6, n7):
            node.refresh_from_db()
        self.assert_chunk(n1, 4, 7)
        self.assert_chunk(n2, 0, 11)
        self.assert_chunk(n3, 5, 6)
        self.assert_chunk(n4, 8, 9)
        self.assert_chunk(n5, 3, 10)
        self.assert_chunk(n6, 12, 13)
        self.assert_chunk(n7, 1, 2)
        n2.set_parent(n6)
        for node in (n1, n2, n3, n4, n5, n6, n7):
            node.refresh_from_db()
        self.assert_chunk(n1, 5, 8)
        self.assert_chunk(n2, 1, 12)
        self.assert_chunk(n3, 6, 7)
        self.assert_chunk(n4, 9, 10)
        self.assert_chunk(n5, 4, 11)
        self.assert_chunk(n6, 0, 13)
        self.assert_chunk(n7, 2, 3)

    def test_deconsolidate(self):
        # ASSUMES CONSOLIDATE IS PASSING
        n1 = NSMTestModel.objects.create(num=1)
        n2 = NSMTestModel.objects.create(num=2)
        n3 = NSMTestModel.objects.create(num=3)
        n4 = NSMTestModel.objects.create(num=4)
        n5 = NSMTestModel.objects.create(num=5)
        n6 = NSMTestModel.objects.create(num=6)
        n7 = NSMTestModel.objects.create(num=7)
        n7.set_parent(n2)
        n4.set_parent(n5)
        n1.set_parent(n5)
        n5.set_parent(n2)
        n3.set_parent(n1)
        n2.set_parent(n6)

        # check that consolidation passed
        for chunk in (
            (n1, 5, 8),
            (n2, 1, 12),
            (n3, 6, 7),
            (n4, 9, 10),
            (n5, 4, 11),
            (n6, 0, 13),
            (n7, 2, 3),
        ):
            chunk[0].refresh_from_db()
            self.assert_chunk(*chunk)

        n4.set_parent(None)
        for chunk in (
            (n1, 5, 8),
            (n2, 1, 10),
            (n3, 6, 7),
            (n4, 12, 13),
            (n5, 4, 9),
            (n6, 0, 11),
            (n7, 2, 3),
        ):
            chunk[0].refresh_from_db()
            self.assert_chunk(*chunk)

        n2.set_parent(None)
        for chunk in (
            (n1, 6, 9),
            (n2, 2, 11),
            (n3, 7, 8),
            (n4, 12, 13),
            (n5, 5, 10),
            (n6, 0, 1),
            (n7, 3, 4),
        ):
            chunk[0].refresh_from_db()
            self.assert_chunk(*chunk)

        n3.set_parent(None)
        for chunk in (
            (n1, 6, 7),
            (n2, 2, 9),
            (n3, 10, 11),
            (n4, 12, 13),
            (n5, 5, 8),
            (n6, 0, 1),
            (n7, 3, 4),
        ):
            chunk[0].refresh_from_db()
            self.assert_chunk(*chunk)

        n7.set_parent(None)
        for chunk in (
            (n1, 6, 7),
            (n2, 4, 9),
            (n3, 10, 11),
            (n4, 12, 13),
            (n5, 5, 8),
            (n6, 0, 1),
            (n7, 2, 3),
        ):
            chunk[0].refresh_from_db()
            self.assert_chunk(*chunk)

        n5.set_parent(None)
        for chunk in (
            (n1, 7, 8),
            (n2, 4, 5),
            (n3, 10, 11),
            (n4, 12, 13),
            (n5, 6, 9),
            (n6, 0, 1),
            (n7, 2, 3),
        ):
            chunk[0].refresh_from_db()
            self.assert_chunk(*chunk)

        n1.set_parent(None)
        for chunk in (
            (n1, 8, 9),
            (n2, 4, 5),
            (n3, 10, 11),
            (n4, 12, 13),
            (n5, 6, 7),
            (n6, 0, 1),
            (n7, 2, 3),
        ):
            chunk[0].refresh_from_db()
            self.assert_chunk(*chunk)

        # nothing happens here, everything is already orphaned
        n6.set_parent(None)
        for chunk in (
            (n1, 8, 9),
            (n2, 4, 5),
            (n3, 10, 11),
            (n4, 12, 13),
            (n5, 6, 7),
            (n6, 0, 1),
            (n7, 2, 3),
        ):
            chunk[0].refresh_from_db()
            self.assert_chunk(*chunk)

    def test_num_children(self):
        n1 = NSMTestModel.objects.create(num=1)
        n2 = NSMTestModel.objects.create(num=2)
        n3 = NSMTestModel.objects.create(num=3)
        n4 = NSMTestModel.objects.create(num=4)
        n5 = NSMTestModel.objects.create(num=5)
        n6 = NSMTestModel.objects.create(num=6)
        n7 = NSMTestModel.objects.create(num=7)
        for node, num_children in zip(
            (n1, n2, n3, n4, n5, n6, n7), (0, 0, 0, 0, 0, 0, 0)
        ):
            self.assertEqual(node.num_children(), num_children)
        n7.set_parent(n2)
        for node, num_children in zip(
            (n1, n2, n3, n4, n5, n6, n7), (0, 1, 0, 0, 0, 0, 0)
        ):
            self.assertEqual(node.num_children(), num_children)
        n4.set_parent(n5)
        for node, num_children in zip(
            (n1, n2, n3, n4, n5, n6, n7), (0, 1, 0, 0, 1, 0, 0)
        ):
            self.assertEqual(node.num_children(), num_children)
        n1.set_parent(n5)
        for node, num_children in zip(
            (n1, n2, n3, n4, n5, n6, n7), (0, 1, 0, 0, 2, 0, 0)
        ):
            self.assertEqual(node.num_children(), num_children)
        n5.set_parent(n2)
        for node, num_children in zip(
            (n1, n2, n3, n4, n5, n6, n7), (0, 4, 0, 0, 2, 0, 0)
        ):
            self.assertEqual(node.num_children(), num_children)
        n3.set_parent(n1)
        for node, num_children in zip(
            (n1, n2, n3, n4, n5, n6, n7), (1, 5, 0, 0, 3, 0, 0)
        ):
            self.assertEqual(node.num_children(), num_children)
        n2.set_parent(n6)
        for node, num_children in zip(
            (n1, n2, n3, n4, n5, n6, n7), (1, 5, 0, 0, 3, 6, 0)
        ):
            self.assertEqual(node.num_children(), num_children)
