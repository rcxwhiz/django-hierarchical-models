import copy

from django.test import TestCase

from django_hierarchical_models.models import Node
from django_hierarchical_models.models.exceptions import CycleException
from tests.models import ExampleModel


def create(num: int, **kwargs) -> ExampleModel:
    return ExampleModel.objects.create(num=num, **kwargs)


class HierarchicalModelSimpleTests(TestCase):
    def test_parent(self):
        parent = create(1)
        child = create(2, parent=parent)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_set_parent(self):
        parent = create(1)
        child = create(2)
        self.assertIsNone(parent.parent())
        self.assertIsNone(child.parent())
        child.num = 3
        child.set_parent(parent)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)
        self.assertEqual(child.num, 3)
        child.refresh_from_db()
        self.assertEqual(child.parent(), parent)
        self.assertEqual(child.num, 2)

    def test_direct_children(self):
        parent = create(1)
        child = create(2, parent=parent)
        _ = create(3)
        self.assertQuerySetEqual(parent.direct_children(), (child,))
        self.assertQuerySetEqual(child.direct_children(), ())

    def test_delete(self):
        parent = create(1)
        child = create(2)
        child.set_parent(parent)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)
        parent.delete()
        child.refresh_from_db()
        self.assertIsNone(child.parent())

    def test_create_cycle(self):
        parent = create(1)
        child = create(2, parent=parent)
        with self.assertRaises(CycleException) as cm:
            parent.set_parent(child)
        self.assertEqual(cm.exception.child, parent)
        self.assertEqual(cm.exception.parent, child)

    def test_ancestors(self):
        parent = create(1)
        child = create(2, parent=parent)
        self.assertListEqual(child.ancestors(), [parent])

    def test_root(self):
        n1 = create(1)
        self.assertEqual(n1.root(), n1)
        n2 = create(2)
        n1.set_parent(n2)
        self.assertEqual(n1.root(), n2)
        self.assertEqual(n2.root(), n2)
        n3 = create(3)
        n2.set_parent(n3)
        self.assertEqual(n1.root(), n3)
        self.assertEqual(n2.root(), n3)
        self.assertEqual(n3.root(), n3)

    def test_children(self):
        n1 = create(1)
        n2 = create(2, parent=n1)
        n3 = create(3, parent=n1)
        expected_children = Node[ExampleModel](
            n1,
            [Node[ExampleModel](n2), Node[ExampleModel](n3)],
        )
        self.assertEqual(
            n1.children(),
            expected_children,
        )

    def test_is_child(self):
        n1 = create(1)
        n2 = create(2)
        self.assertFalse(n1.is_child_of(n2))
        self.assertFalse(n2.is_child_of(n1))
        n2.set_parent(n1)
        self.assertFalse(n1.is_child_of(n2))
        self.assertTrue(n2.is_child_of(n1))

    def test_delete_refresh_behavior(self):
        n1 = create(1)
        n2 = create(2, parent=n1)
        self.assertEqual(n2.parent(), n1)

        n1.delete()

        self.assertEqual(n2.parent(), n1)

        n2.refresh_from_db()

        self.assertIsNone(n2.parent())

    def test_root_refresh_behavior(self):
        n1 = create(1)
        n2 = create(2, parent=n1)
        n3 = create(3, parent=n2)
        n3_copy = ExampleModel.objects.get(pk=n3.pk)

        self.assertEqual(n2.parent(), n1)
        self.assertEqual(n3.root(), n1)
        self.assertEqual(n3_copy.root(), n1)

        n2.set_parent(None)

        self.assertIsNone(n2.parent())

        self.assertEqual(n3.root(), n2)

        self.assertEqual(n3_copy.root(), n1)
        n3_copy.refresh_from_db()
        self.assertEqual(n3_copy.root(), n2)


class HierarchicalModelAdvancedTests(TestCase):
    def setUp(self):
        self.n1 = create(1)
        self.n2 = create(2, parent=self.n1)
        self.n3 = create(3, parent=self.n1)
        self.n4 = create(4, parent=self.n1)
        self.n5 = create(5, parent=self.n2)
        self.n6 = create(6, parent=self.n2)
        self.n7 = create(7, parent=self.n2)
        self.n8 = create(8, parent=self.n3)
        self.n9 = create(9, parent=self.n6)
        self.n10 = create(10, parent=self.n8)
        self.n11 = create(11, parent=self.n10)
        self.n12 = create(12)
        self.n13 = create(13, parent=self.n12)
        self.n14 = create(14, parent=self.n13)
        self.n15 = create(15)
        self.n16 = create(16, parent=self.n15)
        self.n17 = create(17, parent=self.n15)
        self.n18 = create(18)
        self.n19 = create(19)
        self.n20 = create(20)
        self.n21 = create(21, parent=self.n20)
        self.n22 = create(22, parent=self.n20)
        self.n23 = create(23, parent=self.n20)
        self.n24 = create(24, parent=self.n20)
        self.n25 = create(25, parent=self.n20)
        self.n26 = create(26, parent=self.n20)
        self.n27 = create(27, parent=self.n23)
        self.n28 = create(28, parent=self.n23)
        self.n29 = create(29, parent=self.n23)
        self.n30 = create(30, parent=self.n23)
        self.n31 = create(31, parent=self.n23)
        self.n32 = create(32, parent=self.n23)

    def test_parent(self):
        for node, parent in (
            (self.n1, None),
            (self.n2, self.n1),
            (self.n3, self.n1),
            (self.n4, self.n1),
            (self.n5, self.n2),
            (self.n6, self.n2),
            (self.n7, self.n2),
            (self.n8, self.n3),
            (self.n9, self.n6),
            (self.n10, self.n8),
            (self.n11, self.n10),
            (self.n12, None),
            (self.n13, self.n12),
            (self.n14, self.n13),
            (self.n15, None),
            (self.n16, self.n15),
            (self.n17, self.n15),
            (self.n18, None),
            (self.n19, None),
            (self.n20, None),
            (self.n21, self.n20),
            (self.n22, self.n20),
            (self.n23, self.n20),
            (self.n24, self.n20),
            (self.n25, self.n20),
            (self.n26, self.n20),
            (self.n27, self.n23),
            (self.n28, self.n23),
            (self.n29, self.n23),
            (self.n30, self.n23),
            (self.n31, self.n23),
            (self.n32, self.n23),
        ):
            self.assertEqual(node.parent(), parent)

    def test_set_parent(self):
        self.n2.set_parent(None)
        self.assertIsNone(self.n2.parent())
        self.assertEqual(self.n5.parent(), self.n2)
        self.assertEqual(self.n6.parent(), self.n2)
        self.assertEqual(self.n7.parent(), self.n2)

        self.n11.set_parent(self.n13)
        self.assertEqual(self.n11.parent(), self.n13)
        self.assertEqual(self.n13.parent(), self.n12)
        self.assertEqual(self.n14.parent(), self.n13)

        self.n20.set_parent(self.n18)
        self.assertEqual(self.n20.parent(), self.n18)
        self.assertIsNone(self.n18.parent())
        self.assertEqual(self.n21.parent(), self.n20)
        self.assertEqual(self.n22.parent(), self.n20)
        self.assertEqual(self.n23.parent(), self.n20)
        self.assertEqual(self.n24.parent(), self.n20)
        self.assertEqual(self.n25.parent(), self.n20)
        self.assertEqual(self.n26.parent(), self.n20)

    def test_direct_children(self):
        for node in (
            self.n4,
            self.n5,
            self.n7,
            self.n9,
            self.n11,
            self.n14,
            self.n16,
            self.n17,
            self.n18,
            self.n19,
            self.n21,
            self.n22,
            self.n24,
            self.n25,
            self.n26,
            self.n27,
            self.n28,
            self.n29,
            self.n30,
            self.n31,
            self.n32,
        ):
            self.assertQuerySetEqual(node.direct_children(), ())

        self.assertQuerySetEqual(
            self.n1.direct_children(), (self.n2, self.n3, self.n4), ordered=False
        )
        self.assertQuerySetEqual(
            self.n2.direct_children(), (self.n5, self.n6, self.n7), ordered=False
        )
        self.assertQuerySetEqual(self.n3.direct_children(), (self.n8,))
        self.assertQuerySetEqual(self.n6.direct_children(), (self.n9,))
        self.assertQuerySetEqual(self.n8.direct_children(), (self.n10,))
        self.assertQuerySetEqual(self.n10.direct_children(), (self.n11,))
        self.assertQuerySetEqual(self.n12.direct_children(), (self.n13,))
        self.assertQuerySetEqual(self.n13.direct_children(), (self.n14,))
        self.assertQuerySetEqual(
            self.n15.direct_children(), (self.n16, self.n17), ordered=False
        )
        self.assertQuerySetEqual(
            self.n20.direct_children(),
            (self.n21, self.n22, self.n23, self.n24, self.n25, self.n26),
            ordered=False,
        )
        self.assertQuerySetEqual(
            self.n23.direct_children(),
            (self.n27, self.n28, self.n29, self.n30, self.n31, self.n32),
            ordered=False,
        )

    def test_delete(self):
        self.n3.delete()
        for node in (
            self.n1,
            self.n2,
            self.n4,
            self.n5,
            self.n6,
            self.n7,
            self.n8,
            self.n9,
            self.n10,
            self.n11,
            self.n12,
            self.n13,
            self.n14,
            self.n15,
            self.n16,
            self.n17,
            self.n18,
            self.n19,
            self.n20,
            self.n21,
            self.n22,
            self.n23,
            self.n24,
            self.n25,
            self.n26,
            self.n27,
            self.n28,
            self.n29,
            self.n30,
            self.n31,
            self.n32,
        ):
            node.refresh_from_db()
        for node, parent in (
            (self.n1, None),
            (self.n2, self.n1),
            (self.n4, self.n1),
            (self.n5, self.n2),
            (self.n6, self.n2),
            (self.n7, self.n2),
            (self.n8, None),
            (self.n9, self.n6),
            (self.n10, self.n8),
            (self.n11, self.n10),
            (self.n12, None),
            (self.n13, self.n12),
            (self.n14, self.n13),
            (self.n15, None),
            (self.n16, self.n15),
            (self.n17, self.n15),
            (self.n18, None),
            (self.n19, None),
            (self.n20, None),
            (self.n21, self.n20),
            (self.n22, self.n20),
            (self.n23, self.n20),
            (self.n24, self.n20),
            (self.n25, self.n20),
            (self.n26, self.n20),
            (self.n27, self.n23),
            (self.n28, self.n23),
            (self.n29, self.n23),
            (self.n30, self.n23),
            (self.n31, self.n23),
            (self.n32, self.n23),
        ):
            self.assertEqual(node.parent(), parent)

        self.n13.delete()
        for node in (
            self.n1,
            self.n2,
            self.n4,
            self.n5,
            self.n6,
            self.n7,
            self.n8,
            self.n9,
            self.n10,
            self.n11,
            self.n12,
            self.n14,
            self.n15,
            self.n16,
            self.n17,
            self.n18,
            self.n19,
            self.n20,
            self.n21,
            self.n22,
            self.n23,
            self.n24,
            self.n25,
            self.n26,
            self.n27,
            self.n28,
            self.n29,
            self.n30,
            self.n31,
            self.n32,
        ):
            node.refresh_from_db()
        for node, parent in (
            (self.n1, None),
            (self.n2, self.n1),
            (self.n4, self.n1),
            (self.n5, self.n2),
            (self.n6, self.n2),
            (self.n7, self.n2),
            (self.n8, None),
            (self.n9, self.n6),
            (self.n10, self.n8),
            (self.n11, self.n10),
            (self.n12, None),
            (self.n14, None),
            (self.n15, None),
            (self.n16, self.n15),
            (self.n17, self.n15),
            (self.n18, None),
            (self.n19, None),
            (self.n20, None),
            (self.n21, self.n20),
            (self.n22, self.n20),
            (self.n23, self.n20),
            (self.n24, self.n20),
            (self.n25, self.n20),
            (self.n26, self.n20),
            (self.n27, self.n23),
            (self.n28, self.n23),
            (self.n29, self.n23),
            (self.n30, self.n23),
            (self.n31, self.n23),
            (self.n32, self.n23),
        ):
            self.assertEqual(node.parent(), parent)

        self.n20.delete()
        for node in (
            self.n1,
            self.n2,
            self.n4,
            self.n5,
            self.n6,
            self.n7,
            self.n8,
            self.n9,
            self.n10,
            self.n11,
            self.n12,
            self.n14,
            self.n15,
            self.n16,
            self.n17,
            self.n18,
            self.n19,
            self.n21,
            self.n22,
            self.n23,
            self.n24,
            self.n25,
            self.n26,
            self.n27,
            self.n28,
            self.n29,
            self.n30,
            self.n31,
            self.n32,
        ):
            node.refresh_from_db()
        for node, parent in (
            (self.n1, None),
            (self.n2, self.n1),
            (self.n4, self.n1),
            (self.n5, self.n2),
            (self.n6, self.n2),
            (self.n7, self.n2),
            (self.n8, None),
            (self.n9, self.n6),
            (self.n10, self.n8),
            (self.n11, self.n10),
            (self.n12, None),
            (self.n14, None),
            (self.n15, None),
            (self.n16, self.n15),
            (self.n17, self.n15),
            (self.n18, None),
            (self.n19, None),
            (self.n21, None),
            (self.n22, None),
            (self.n23, None),
            (self.n24, None),
            (self.n25, None),
            (self.n26, None),
            (self.n27, self.n23),
            (self.n28, self.n23),
            (self.n29, self.n23),
            (self.n30, self.n23),
            (self.n31, self.n23),
            (self.n32, self.n23),
        ):
            self.assertEqual(node.parent(), parent)

        self.n6.delete()
        for node in (
            self.n1,
            self.n2,
            self.n4,
            self.n5,
            self.n7,
            self.n8,
            self.n9,
            self.n10,
            self.n11,
            self.n12,
            self.n14,
            self.n15,
            self.n16,
            self.n17,
            self.n18,
            self.n19,
            self.n21,
            self.n22,
            self.n23,
            self.n24,
            self.n25,
            self.n26,
            self.n27,
            self.n28,
            self.n29,
            self.n30,
            self.n31,
            self.n32,
        ):
            node.refresh_from_db()
        for node, parent in (
            (self.n1, None),
            (self.n2, self.n1),
            (self.n4, self.n1),
            (self.n5, self.n2),
            (self.n7, self.n2),
            (self.n8, None),
            (self.n9, None),
            (self.n10, self.n8),
            (self.n11, self.n10),
            (self.n12, None),
            (self.n14, None),
            (self.n15, None),
            (self.n16, self.n15),
            (self.n17, self.n15),
            (self.n18, None),
            (self.n19, None),
            (self.n21, None),
            (self.n22, None),
            (self.n23, None),
            (self.n24, None),
            (self.n25, None),
            (self.n26, None),
            (self.n27, self.n23),
            (self.n28, self.n23),
            (self.n29, self.n23),
            (self.n30, self.n23),
            (self.n31, self.n23),
            (self.n32, self.n23),
        ):
            self.assertEqual(node.parent(), parent)

    def test_create_cycle(self):
        with self.assertRaises(CycleException) as cm:
            self.n1.set_parent(self.n10)
        self.assertEqual(cm.exception.child, self.n1)
        self.assertEqual(cm.exception.parent, self.n10)

        with self.assertRaises(CycleException) as cm:
            self.n12.set_parent(self.n14)
        self.assertEqual(cm.exception.child, self.n12)
        self.assertEqual(cm.exception.parent, self.n14)

        with self.assertRaises(CycleException) as cm:
            self.n18.set_parent(self.n18)
        self.assertEqual(cm.exception.child, self.n18)
        self.assertEqual(cm.exception.parent, self.n18)

        with self.assertRaises(CycleException) as cm:
            self.n20.set_parent(self.n21)
        self.assertEqual(cm.exception.child, self.n20)
        self.assertEqual(cm.exception.parent, self.n21)

    def test_ancestors(self):
        for node, ancestors in (
            (self.n1, []),
            (self.n2, [self.n1]),
            (self.n3, [self.n1]),
            (self.n4, [self.n1]),
            (self.n5, [self.n2, self.n1]),
            (self.n6, [self.n2, self.n1]),
            (self.n7, [self.n2, self.n1]),
            (self.n8, [self.n3, self.n1]),
            (self.n9, [self.n6, self.n2, self.n1]),
            (self.n10, [self.n8, self.n3, self.n1]),
            (self.n11, [self.n10, self.n8, self.n3, self.n1]),
            (self.n12, []),
            (self.n13, [self.n12]),
            (self.n14, [self.n13, self.n12]),
            (self.n15, []),
            (self.n16, [self.n15]),
            (self.n17, [self.n15]),
            (self.n19, []),
            (self.n20, []),
            (self.n21, [self.n20]),
            (self.n22, [self.n20]),
            (self.n23, [self.n20]),
            (self.n24, [self.n20]),
            (self.n25, [self.n20]),
            (self.n26, [self.n20]),
            (self.n27, [self.n23, self.n20]),
            (self.n28, [self.n23, self.n20]),
            (self.n29, [self.n23, self.n20]),
            (self.n30, [self.n23, self.n20]),
            (self.n31, [self.n23, self.n20]),
            (self.n32, [self.n23, self.n20]),
        ):
            self.assertListEqual(node.ancestors(), ancestors)

    def test_ancestor_options(self):
        self.assertListEqual(self.n11.ancestors(max_level=0), [])
        self.assertListEqual(self.n11.ancestors(max_level=1), [self.n10])
        self.assertListEqual(self.n11.ancestors(max_level=2), [self.n10, self.n8])
        self.assertListEqual(
            self.n11.ancestors(max_level=3), [self.n10, self.n8, self.n3]
        )
        self.assertListEqual(
            self.n11.ancestors(max_level=4), [self.n10, self.n8, self.n3, self.n1]
        )
        self.assertListEqual(
            self.n11.ancestors(max_level=5), [self.n10, self.n8, self.n3, self.n1]
        )

    def test_root(self):
        for node, root in (
            (self.n1, self.n1),
            (self.n2, self.n1),
            (self.n3, self.n1),
            (self.n4, self.n1),
            (self.n5, self.n1),
            (self.n6, self.n1),
            (self.n7, self.n1),
            (self.n8, self.n1),
            (self.n9, self.n1),
            (self.n10, self.n1),
            (self.n11, self.n1),
            (self.n12, self.n12),
            (self.n13, self.n12),
            (self.n14, self.n12),
            (self.n15, self.n15),
            (self.n16, self.n15),
            (self.n17, self.n15),
            (self.n18, self.n18),
            (self.n19, self.n19),
            (self.n20, self.n20),
            (self.n21, self.n20),
            (self.n22, self.n20),
            (self.n23, self.n20),
            (self.n24, self.n20),
            (self.n25, self.n20),
            (self.n26, self.n20),
            (self.n27, self.n20),
            (self.n28, self.n20),
            (self.n29, self.n20),
            (self.n30, self.n20),
            (self.n31, self.n20),
            (self.n32, self.n20),
        ):
            self.assertEqual(node.root(), root)

    def test_is_child(self):
        for parent, child in (
            (self.n1, self.n9),
            (self.n2, self.n9),
            (self.n6, self.n9),
            (self.n13, self.n14),
            (self.n12, self.n14),
            (self.n12, self.n13),
            (self.n20, self.n26),
            (self.n23, self.n30),
            (self.n20, self.n30),
        ):
            self.assertTrue(child.is_child_of(parent))

        for parent, child in (
            (self.n3, self.n9),
            (self.n5, self.n9),
            (self.n14, self.n13),
            (self.n14, self.n12),
            (self.n13, self.n12),
            (self.n26, self.n20),
            (self.n24, self.n30),
            (self.n31, self.n30),
            (self.n1, self.n1),
            (self.n16, self.n16),
            (self.n32, self.n32),
        ):
            self.assertFalse(child.is_child_of(parent))

    def test_advanced_children(self):
        mn1 = Node[ExampleModel](self.n1)
        mn2 = Node[ExampleModel](self.n2)
        mn3 = Node[ExampleModel](self.n3)
        mn4 = Node[ExampleModel](self.n4)
        mn5 = Node[ExampleModel](self.n5)
        mn6 = Node[ExampleModel](self.n6)
        mn7 = Node[ExampleModel](self.n7)
        mn8 = Node[ExampleModel](self.n8)
        mn9 = Node[ExampleModel](self.n9)
        mn10 = Node[ExampleModel](self.n10)
        mn11 = Node[ExampleModel](self.n11)
        mn12 = Node[ExampleModel](self.n12)
        mn13 = Node[ExampleModel](self.n13)
        mn14 = Node[ExampleModel](self.n14)
        mn15 = Node[ExampleModel](self.n15)
        mn16 = Node[ExampleModel](self.n16)
        mn17 = Node[ExampleModel](self.n17)
        mn18 = Node[ExampleModel](self.n18)
        mn19 = Node[ExampleModel](self.n19)
        mn20 = Node[ExampleModel](self.n20)
        mn21 = Node[ExampleModel](self.n21)
        mn22 = Node[ExampleModel](self.n22)
        mn23 = Node[ExampleModel](self.n23)
        mn24 = Node[ExampleModel](self.n24)
        mn25 = Node[ExampleModel](self.n25)
        mn26 = Node[ExampleModel](self.n26)
        mn27 = Node[ExampleModel](self.n27)
        mn28 = Node[ExampleModel](self.n28)
        mn29 = Node[ExampleModel](self.n29)
        mn30 = Node[ExampleModel](self.n30)
        mn31 = Node[ExampleModel](self.n31)
        mn32 = Node[ExampleModel](self.n32)

        mn1.children = [mn2, mn3, mn4]
        mn2.children = [mn5, mn6, mn7]
        mn3.children = [mn8]
        mn6.children = [mn9]
        mn8.children = [mn10]
        mn10.children = [mn11]

        mn12.children = [mn13]
        mn13.children = [mn14]

        mn15.children = [mn16, mn17]

        mn20.children = [mn21, mn22, mn23, mn24, mn25, mn26]
        mn23.children = [mn27, mn28, mn29, mn30, mn31, mn32]

        self.assertEqual(
            self.n1.children(sibling_transform=lambda x: x.order_by("num")), mn1
        )
        self.assertEqual(
            self.n2.children(sibling_transform=lambda x: x.order_by("num")), mn2
        )
        self.assertEqual(
            self.n3.children(sibling_transform=lambda x: x.order_by("num")), mn3
        )
        self.assertEqual(
            self.n4.children(sibling_transform=lambda x: x.order_by("num")), mn4
        )
        self.assertEqual(
            self.n5.children(sibling_transform=lambda x: x.order_by("num")), mn5
        )
        self.assertEqual(
            self.n6.children(sibling_transform=lambda x: x.order_by("num")), mn6
        )
        self.assertEqual(
            self.n7.children(sibling_transform=lambda x: x.order_by("num")), mn7
        )
        self.assertEqual(
            self.n8.children(sibling_transform=lambda x: x.order_by("num")), mn8
        )
        self.assertEqual(
            self.n9.children(sibling_transform=lambda x: x.order_by("num")), mn9
        )
        self.assertEqual(
            self.n10.children(sibling_transform=lambda x: x.order_by("num")), mn10
        )
        self.assertEqual(
            self.n11.children(sibling_transform=lambda x: x.order_by("num")), mn11
        )
        self.assertEqual(
            self.n12.children(sibling_transform=lambda x: x.order_by("num")), mn12
        )
        self.assertEqual(
            self.n13.children(sibling_transform=lambda x: x.order_by("num")), mn13
        )
        self.assertEqual(
            self.n14.children(sibling_transform=lambda x: x.order_by("num")), mn14
        )
        self.assertEqual(
            self.n15.children(sibling_transform=lambda x: x.order_by("num")), mn15
        )
        self.assertEqual(
            self.n16.children(sibling_transform=lambda x: x.order_by("num")), mn16
        )
        self.assertEqual(
            self.n17.children(sibling_transform=lambda x: x.order_by("num")), mn17
        )
        self.assertEqual(
            self.n18.children(sibling_transform=lambda x: x.order_by("num")), mn18
        )
        self.assertEqual(
            self.n19.children(sibling_transform=lambda x: x.order_by("num")), mn19
        )
        self.assertEqual(
            self.n20.children(sibling_transform=lambda x: x.order_by("num")), mn20
        )
        self.assertEqual(
            self.n21.children(sibling_transform=lambda x: x.order_by("num")), mn21
        )
        self.assertEqual(
            self.n22.children(sibling_transform=lambda x: x.order_by("num")), mn22
        )
        self.assertEqual(
            self.n23.children(sibling_transform=lambda x: x.order_by("num")), mn23
        )
        self.assertEqual(
            self.n24.children(sibling_transform=lambda x: x.order_by("num")), mn24
        )
        self.assertEqual(
            self.n25.children(sibling_transform=lambda x: x.order_by("num")), mn25
        )
        self.assertEqual(
            self.n26.children(sibling_transform=lambda x: x.order_by("num")), mn26
        )
        self.assertEqual(
            self.n27.children(sibling_transform=lambda x: x.order_by("num")), mn27
        )
        self.assertEqual(
            self.n28.children(sibling_transform=lambda x: x.order_by("num")), mn28
        )
        self.assertEqual(
            self.n29.children(sibling_transform=lambda x: x.order_by("num")), mn29
        )
        self.assertEqual(
            self.n30.children(sibling_transform=lambda x: x.order_by("num")), mn30
        )
        self.assertEqual(
            self.n31.children(sibling_transform=lambda x: x.order_by("num")), mn31
        )
        self.assertEqual(
            self.n32.children(sibling_transform=lambda x: x.order_by("num")), mn32
        )

    def test_advanced_children_options(self):
        mn1 = Node[ExampleModel](self.n1)
        mn2 = Node[ExampleModel](self.n2)
        mn3 = Node[ExampleModel](self.n3)
        mn4 = Node[ExampleModel](self.n4)
        mn5 = Node[ExampleModel](self.n5)
        mn6 = Node[ExampleModel](self.n6)
        mn7 = Node[ExampleModel](self.n7)
        mn8 = Node[ExampleModel](self.n8)
        mn9 = Node[ExampleModel](self.n9)
        mn10 = Node[ExampleModel](self.n10)
        mn11 = Node[ExampleModel](self.n11)
        mn12 = Node[ExampleModel](self.n12)
        mn13 = Node[ExampleModel](self.n13)
        mn14 = Node[ExampleModel](self.n14)
        mn15 = Node[ExampleModel](self.n15)
        mn16 = Node[ExampleModel](self.n16)
        mn17 = Node[ExampleModel](self.n17)
        mn20 = Node[ExampleModel](self.n20)
        mn21 = Node[ExampleModel](self.n21)
        mn22 = Node[ExampleModel](self.n22)
        mn23 = Node[ExampleModel](self.n23)
        mn24 = Node[ExampleModel](self.n24)
        mn25 = Node[ExampleModel](self.n25)
        mn26 = Node[ExampleModel](self.n26)
        mn27 = Node[ExampleModel](self.n27)
        mn28 = Node[ExampleModel](self.n28)
        mn29 = Node[ExampleModel](self.n29)
        mn30 = Node[ExampleModel](self.n30)
        mn31 = Node[ExampleModel](self.n31)
        mn32 = Node[ExampleModel](self.n32)

        mn1.children = [mn2, mn3, mn4]
        mn2.children = [mn5, mn6, mn7]
        mn3.children = [mn8]
        mn6.children = [mn9]
        mn8.children = [mn10]
        mn10.children = [mn11]

        mn12.children = [mn13]
        mn13.children = [mn14]

        mn15.children = [mn16, mn17]

        mn20.children = [mn21, mn22, mn23, mn24, mn25, mn26]
        mn23.children = [mn27, mn28, mn29, mn30, mn31, mn32]

        t1 = copy.copy(mn1)
        t1.children[0].children[1].children = []
        t1.children[1].children[0].children = []

        self.assertEqual(
            self.n1.children(
                max_generations=2, sibling_transform=lambda x: x.order_by("num")
            ),
            t1,
        )

        t2 = copy.copy(mn1)
        t2.children = t2.children[:2]
        t2.children[0].children = t2.children[0].children[:2]

        self.assertEqual(
            self.n1.children(
                max_siblings=2, sibling_transform=lambda x: x.order_by("num")
            ),
            t2,
        )

        t3 = copy.copy(mn1)
        t3.children[0].children = t3.children[0].children[:2]
        t3.children[0].children[1].children = []
        t3.children[1].children = []

        self.assertEqual(
            self.n1.children(
                max_total=6, sibling_transform=lambda x: x.order_by("num")
            ),
            t3,
        )

        t4 = copy.copy(mn1)
        t4.children = t4.children[:2]
        t4.children[0].children = t4.children[0].children[:2]
        t4.children[1].children[0].children[0].children = []

        self.assertEqual(
            self.n1.children(
                max_generations=3,
                max_siblings=2,
                sibling_transform=lambda x: x.order_by("num"),
            ),
            t4,
        )

        t5 = copy.copy(mn20)
        t5.children = t5.children[:3]
        t5.children[2].children = []

        self.assertEqual(
            self.n20.children(
                max_generations=1,
                max_siblings=3,
                sibling_transform=lambda x: x.order_by("num"),
            ),
            t5,
        )

        t6 = copy.copy(mn20)
        t6.children = t6.children[:4]
        t6.children[2].children = t6.children[2].children[:1]

        self.assertEqual(
            self.n20.children(
                max_siblings=4,
                max_total=6,
                sibling_transform=lambda x: x.order_by("num"),
            ),
            t6,
        )

        t7 = copy.copy(mn1)
        t7.children = t7.children[:2]
        t7.children[0].children = t7.children[0].children[:2]
        t7.children[1].children[0].children = []

        self.assertEqual(
            self.n1.children(
                max_generations=3,
                max_siblings=2,
                max_total=7,
                sibling_transform=lambda x: x.order_by("num"),
            ),
            t7,
        )

        self.assertEqual(
            self.n15.children(
                max_generations=4, sibling_transform=lambda x: x.order_by("num")
            ),
            mn15,
        )
        self.assertEqual(
            self.n15.children(
                max_siblings=5, sibling_transform=lambda x: x.order_by("num")
            ),
            mn15,
        )
        self.assertEqual(
            self.n15.children(
                max_total=10, sibling_transform=lambda x: x.order_by("num")
            ),
            mn15,
        )
        self.assertEqual(
            self.n15.children(
                max_generations=4,
                max_siblings=5,
                sibling_transform=lambda x: x.order_by("num"),
            ),
            mn15,
        )
        self.assertEqual(
            self.n15.children(
                max_generations=4,
                max_total=10,
                sibling_transform=lambda x: x.order_by("num"),
            ),
            mn15,
        )
        self.assertEqual(
            self.n15.children(
                max_siblings=5,
                max_total=10,
                sibling_transform=lambda x: x.order_by("num"),
            ),
            mn15,
        )
        self.assertEqual(
            self.n15.children(
                max_generations=4,
                max_siblings=5,
                max_total=10,
                sibling_transform=lambda x: x.order_by("num"),
            ),
            mn15,
        )
