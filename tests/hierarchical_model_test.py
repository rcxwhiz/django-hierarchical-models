from typing import TypeVar

from django.test import TestCase

from django_hierarchical_models.models.exceptions import (
    AlreadyHasParentException,
    NotAChildException,
)
from django_hierarchical_models.models.hierarchical_model import HierarchicalModel
from tests.models import TestModelMixin


class TestHierarchicalModel(TestModelMixin, HierarchicalModel):
    pass


T = TypeVar("T", bound=TestHierarchicalModel)


class HierarchicalModelTestCase(TestCase):
    model_class: T

    def create(self, num: int, **kwargs) -> T:
        # convenience method to save num= in create calls
        return self.model_class.objects.create(num=num, **kwargs)

    def setUp(self):
        self.n1 = self.create(1)
        self.n2 = self.create(2)
        self.n3 = self.create(3)
        self.n4 = self.create(4)
        self.n5 = self.create(5)
        self.n6 = self.create(6)
        self.n7 = self.create(7)
        self.n8 = self.create(8)
        self.n9 = self.create(9)
        self.n10 = self.create(10)
        self.n11 = self.create(11)
        self.n12 = self.create(12)
        self.n13 = self.create(13)
        self.n14 = self.create(14)
        self.n15 = self.create(15)
        self.n16 = self.create(16)
        self.n17 = self.create(17)
        self.n18 = self.create(18)
        self.n19 = self.create(19)
        self.n20 = self.create(20)
        self.n21 = self.create(21)
        self.n22 = self.create(22)
        self.n23 = self.create(23)
        self.n24 = self.create(24)
        self.n25 = self.create(25)
        self.n26 = self.create(26)
        self.n27 = self.create(27)
        self.n28 = self.create(28)
        self.n29 = self.create(29)
        self.n30 = self.create(30)
        self.n31 = self.create(31)
        self.n32 = self.create(32)

        self.n2.set_parent(self.n1)
        self.n3.set_parent(self.n1)
        self.n4.set_parent(self.n1)

        self.n5.set_parent(self.n2)
        self.n6.set_parent(self.n2)
        self.n7.set_parent(self.n2)

        self.n8.set_parent(self.n3)

        self.n9.set_parent(self.n6)

        self.n10.set_parent(self.n8)

        self.n11.set_parent(self.n10)

        self.n13.set_parent(self.n12)

        self.n14.set_parent(self.n13)

        self.n16.set_parent(self.n15)
        self.n17.set_parent(self.n15)

        self.n21.set_parent(self.n20)
        self.n22.set_parent(self.n20)
        self.n23.set_parent(self.n20)
        self.n24.set_parent(self.n20)
        self.n25.set_parent(self.n20)
        self.n26.set_parent(self.n20)

        self.n27.set_parent(self.n23)
        self.n28.set_parent(self.n23)
        self.n29.set_parent(self.n23)
        self.n30.set_parent(self.n23)
        self.n31.set_parent(self.n23)
        self.n32.set_parent(self.n23)

    def test_basic_parent(self):
        parent = self.create(1)
        child = self.create(2, parent=parent)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_basic_set_parent(self):
        parent = self.create(1)
        child = self.create(2)
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

    def test_basic_direct_children(self):
        parent = self.create(1)
        child = self.create(2, parent=parent)
        self.assertQuerySetEqual(parent.direct_children(), {child})

    def test_basic_child_transform(self):
        n1 = self.create(1)
        n2 = n1.create_child(num=2)
        n3 = n1.create_child(num=3)
        self.assertQuerySetEqual(
            n1.direct_children(transform=lambda x: x.order_by("num")), [n2, n3]
        )
        self.assertQuerySetEqual(
            n1.direct_children(transform=lambda x: x.order_by("-num")), [n3, n2]
        )

    def test_basic_create_child(self):
        parent = self.create(1)
        child = parent.create_child(num=2)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_basic_add_child(self):
        n1 = self.create(1)
        n2 = self.create(2)
        n1.add_child(n2)
        self.assertEqual(n2.parent(), n1)
        n3 = self.create(3)
        with self.assertRaises(AlreadyHasParentException) as cm:
            n3.add_child(n2, check_has_parent=True)
        self.assertEqual(cm.exception.child, n2)
        self.assertEqual(n2.parent(), n1)
        n3.add_child(n2)
        self.assertEqual(n2.parent(), n3)

    def test_basic_remove_child(self):
        parent = self.create(1)
        child = self.create(2, parent=parent)
        parent.remove_child(child)
        self.assertIsNone(child.parent())
        with self.assertRaises(NotAChildException) as cm:
            parent.remove_child(child, check_is_child=True)
        self.assertEqual(cm.exception.child, child)
        self.assertEqual(cm.exception.parent, parent)
        self.assertIsNone(child.parent())
        parent.remove_child(child)
        self.assertIsNone(child.parent())

    def test_basic_ancestors(self):
        parent = self.create(1)
        child = self.create(2, parent=parent)
        self.assertListEqual(child.ancestors(), [parent])

    def test_basic_root(self):
        n1 = self.create(1)
        self.assertEqual(n1.root(), n1)
        n2 = self.create(2)
        n1.set_parent(n2)
        self.assertEqual(n1.root(), n2)
        n3 = self.create(3)
        n2.set_parent(n3)
        self.assertEqual(n1.root(), n3)

    def test_basic_children(self):
        n1 = self.create(1)
        n2 = n1.create_child(num=2)
        n3 = n1.create_child(num=3)
        expected_children = HierarchicalModel.Node(
            n1, [HierarchicalModel.Node(n2), HierarchicalModel.Node(n3)]
        )
        self.assertEqual(
            n1.children(sibling_transform=lambda x: x.order_by("num")),
            expected_children,
        )

    def test_advanced_parent(self):
        self.assertIsNone(self.n1.parent())
        self.assertEqual(self.n2.parent(), self.n1)
        self.assertEqual(self.n3.parent(), self.n1)
        self.assertEqual(self.n4.parent(), self.n1)
        self.assertEqual(self.n5.parent(), self.n2)
        self.assertEqual(self.n6.parent(), self.n2)
        self.assertEqual(self.n7.parent(), self.n2)
        self.assertEqual(self.n8.parent(), self.n3)
        self.assertEqual(self.n9.parent(), self.n6)
        self.assertEqual(self.n10.parent(), self.n8)
        self.assertEqual(self.n11.parent(), self.n10)
        self.assertIsNone(self.n12.parent())
        self.assertEqual(self.n13.parent(), self.n12)
        self.assertEqual(self.n14.parent(), self.n13)
        self.assertIsNone(self.n15.parent())
        self.assertEqual(self.n16.parent(), self.n15)
        self.assertEqual(self.n17.parent(), self.n15)
        self.assertIsNone(self.n18.parent())
        self.assertIsNone(self.n19.parent())
        self.assertIsNone(self.n20.parent())
        self.assertEqual(self.n21.parent(), self.n20)
        self.assertEqual(self.n22.parent(), self.n20)
        self.assertEqual(self.n23.parent(), self.n20)
        self.assertEqual(self.n24.parent(), self.n20)
        self.assertEqual(self.n25.parent(), self.n20)
        self.assertEqual(self.n26.parent(), self.n20)
        self.assertEqual(self.n27.parent(), self.n23)
        self.assertEqual(self.n28.parent(), self.n23)
        self.assertEqual(self.n29.parent(), self.n23)
        self.assertEqual(self.n30.parent(), self.n23)
        self.assertEqual(self.n31.parent(), self.n23)
        self.assertEqual(self.n32.parent(), self.n23)

    def test_advanced_set_parent(self):
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

    def test_advanced_direct_children(self):
        self.assertQuerySetEqual(
            self.n1.direct_children(), [self.n2, self.n3, self.n4], ordered=False
        )
        self.assertQuerySetEqual(
            self.n2.direct_children(), [self.n5, self.n6, self.n7], ordered=False
        )
        self.assertQuerySetEqual(self.n3.direct_children(), [self.n8])
        self.assertQuerySetEqual(self.n4.direct_children(), [])
        self.assertQuerySetEqual(self.n5.direct_children(), [])
        self.assertQuerySetEqual(self.n6.direct_children(), [self.n9])
        self.assertQuerySetEqual(self.n7.direct_children(), [])
        self.assertQuerySetEqual(self.n8.direct_children(), [self.n10])
        self.assertQuerySetEqual(self.n9.direct_children(), [])
        self.assertQuerySetEqual(self.n10.direct_children(), [self.n11])
        self.assertQuerySetEqual(self.n11.direct_children(), [])
        self.assertQuerySetEqual(self.n12.direct_children(), [self.n13])
        self.assertQuerySetEqual(self.n13.direct_children(), [self.n14])
        self.assertQuerySetEqual(self.n14.direct_children(), [])
        self.assertQuerySetEqual(
            self.n15.direct_children(), [self.n16, self.n17], ordered=False
        )
        self.assertQuerySetEqual(self.n16.direct_children(), [])
        self.assertQuerySetEqual(self.n17.direct_children(), [])
        self.assertQuerySetEqual(self.n18.direct_children(), [])
        self.assertQuerySetEqual(self.n19.direct_children(), [])
        self.assertQuerySetEqual(
            self.n20.direct_children(),
            [self.n21, self.n22, self.n23, self.n24, self.n25, self.n26],
            ordered=False,
        )
        self.assertQuerySetEqual(self.n21.direct_children(), [])
        self.assertQuerySetEqual(self.n22.direct_children(), [])
        self.assertQuerySetEqual(
            self.n23.direct_children(),
            [self.n27, self.n28, self.n29, self.n30, self.n31, self.n32],
            ordered=False,
        )
        self.assertQuerySetEqual(self.n24.direct_children(), [])
        self.assertQuerySetEqual(self.n25.direct_children(), [])
        self.assertQuerySetEqual(self.n26.direct_children(), [])
        self.assertQuerySetEqual(self.n27.direct_children(), [])
        self.assertQuerySetEqual(self.n28.direct_children(), [])
        self.assertQuerySetEqual(self.n29.direct_children(), [])
        self.assertQuerySetEqual(self.n30.direct_children(), [])
        self.assertQuerySetEqual(self.n31.direct_children(), [])
        self.assertQuerySetEqual(self.n32.direct_children(), [])

    def test_advanced_child_transform(self):
        self.assertQuerySetEqual(
            self.n1.direct_children(transform=lambda x: x.order_by("-num")),
            [self.n4, self.n3, self.n2],
        )
        self.assertQuerySetEqual(
            self.n2.direct_children(
                transform=lambda x: x.filter(num__gt=5).order_by("num")
            ),
            [self.n6, self.n7],
        )
        self.assertQuerySetEqual(
            self.n20.direct_children(
                transform=lambda x: x.filter(num__gt=21, num__lt=26)
            ),
            [self.n22, self.n23, self.n24, self.n25],
            ordered=False,
        )

    def test_advanced_create_child(self):
        n33 = self.n1.create_child(num=33)
        self.assertEqual(n33.parent(), self.n1)
        self.assertQuerySetEqual(
            self.n1.direct_children(), [self.n2, self.n3, self.n4, n33], ordered=False
        )
        self.assertEqual(self.n2.parent(), self.n1)
        self.assertEqual(self.n3.parent(), self.n1)
        self.assertEqual(self.n4.parent(), self.n1)

    def test_advanced_add_child(self):
        self.n1.add_child(self.n18)
        self.assertEqual(self.n18.parent(), self.n1)
        self.assertQuerySetEqual(
            self.n1.direct_children(),
            [self.n2, self.n3, self.n4, self.n18],
            ordered=False,
        )
        self.assertQuerySetEqual(self.n18.direct_children(), [])
        self.n12.add_child(self.n15)
        self.assertEqual(self.n15.parent(), self.n12)
        self.assertQuerySetEqual(
            self.n12.direct_children(), [self.n13, self.n15], ordered=False
        )
        self.assertQuerySetEqual(
            self.n15.direct_children(), [self.n16, self.n17], ordered=False
        )
        with self.assertRaises(AlreadyHasParentException) as cm:
            self.n19.add_child(self.n21, check_has_parent=True)
        self.assertEqual(cm.exception.child, self.n21)
        self.assertEqual(self.n21.parent(), self.n20)
        self.assertQuerySetEqual(self.n19.direct_children(), [])
        self.n19.add_child(self.n21)
        self.assertEqual(self.n21.parent(), self.n19)
        self.assertQuerySetEqual(self.n19.direct_children(), [self.n21])
        self.assertQuerySetEqual(self.n21.direct_children(), [])
        self.assertQuerySetEqual(
            self.n20.direct_children(),
            [self.n22, self.n23, self.n24, self.n25, self.n26],
            ordered=False,
        )

    def test_advanced_remove_child(self):
        self.n1.remove_child(self.n3)
        self.assertIsNone(self.n3.parent())
        self.assertQuerySetEqual(
            self.n1.direct_children(), [self.n2, self.n4], ordered=False
        )
        self.assertQuerySetEqual(self.n3.direct_children(), [self.n8])
        self.n20.remove_child(self.n23)
        self.assertIsNone(self.n23.parent())
        self.assertQuerySetEqual(
            self.n20.direct_children(),
            [self.n21, self.n22, self.n24, self.n25, self.n26],
            ordered=False,
        )
        self.assertQuerySetEqual(
            self.n23.direct_children(),
            [self.n27, self.n28, self.n29, self.n30, self.n31, self.n32],
            ordered=False,
        )
        with self.assertRaises(NotAChildException) as cm:
            self.n18.remove_child(self.n12, check_is_child=True)
        self.assertEqual(cm.exception.child, self.n12)
        self.assertEqual(cm.exception.parent, self.n18)
        self.assertIsNone(self.n12.parent())
        self.assertQuerySetEqual(self.n18.direct_children(), [])
        self.assertQuerySetEqual(self.n12.direct_children(), [self.n13])
        with self.assertRaises(NotAChildException) as cm:
            self.n18.remove_child(self.n14, check_is_child=True)
        self.assertEqual(cm.exception.child, self.n14)
        self.assertEqual(cm.exception.parent, self.n18)
        self.assertEqual(self.n14.parent(), self.n13)
        self.assertQuerySetEqual(self.n18.direct_children(), [])
        self.assertQuerySetEqual(self.n14.direct_children(), [])
        self.n6.remove_child(self.n10)
        self.assertEqual(self.n10.parent(), self.n8)
        self.assertQuerySetEqual(self.n6.direct_children(), [self.n9])
        self.assertQuerySetEqual(self.n8.direct_children(), [self.n10])
        self.assertQuerySetEqual(self.n10.direct_children(), [self.n11])

    def test_advanced_ancestors(self):
        self.assertListEqual(self.n1.ancestors(), [])
        self.assertListEqual(self.n2.ancestors(), [self.n1])
        self.assertListEqual(self.n3.ancestors(), [self.n1])
        self.assertListEqual(self.n4.ancestors(), [self.n1])
        self.assertListEqual(self.n5.ancestors(), [self.n2, self.n1])
        self.assertListEqual(self.n6.ancestors(), [self.n2, self.n1])
        self.assertListEqual(self.n7.ancestors(), [self.n2, self.n1])
        self.assertListEqual(self.n8.ancestors(), [self.n3, self.n1])
        self.assertListEqual(self.n9.ancestors(), [self.n6, self.n2, self.n1])
        self.assertListEqual(self.n10.ancestors(), [self.n8, self.n3, self.n1])
        self.assertListEqual(
            self.n11.ancestors(), [self.n10, self.n8, self.n3, self.n1]
        )
        self.assertListEqual(self.n12.ancestors(), [])
        self.assertListEqual(self.n13.ancestors(), [self.n12])
        self.assertListEqual(self.n14.ancestors(), [self.n13, self.n12])
        self.assertListEqual(self.n15.ancestors(), [])
        self.assertListEqual(self.n16.ancestors(), [self.n15])
        self.assertListEqual(self.n17.ancestors(), [self.n15])
        self.assertListEqual(self.n18.ancestors(), [])
        self.assertListEqual(self.n19.ancestors(), [])
        self.assertListEqual(self.n20.ancestors(), [])
        self.assertListEqual(self.n21.ancestors(), [self.n20])
        self.assertListEqual(self.n22.ancestors(), [self.n20])
        self.assertListEqual(self.n23.ancestors(), [self.n20])
        self.assertListEqual(self.n24.ancestors(), [self.n20])
        self.assertListEqual(self.n25.ancestors(), [self.n20])
        self.assertListEqual(self.n26.ancestors(), [self.n20])
        self.assertListEqual(self.n27.ancestors(), [self.n23, self.n20])
        self.assertListEqual(self.n28.ancestors(), [self.n23, self.n20])
        self.assertListEqual(self.n29.ancestors(), [self.n23, self.n20])
        self.assertListEqual(self.n30.ancestors(), [self.n23, self.n20])
        self.assertListEqual(self.n31.ancestors(), [self.n23, self.n20])
        self.assertListEqual(self.n32.ancestors(), [self.n23, self.n20])

    def test_advanced_ancestors_options(self):
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

    def test_advanced_root(self):
        self.assertEqual(self.n1.root(), self.n1)
        self.assertEqual(self.n2.root(), self.n1)
        self.assertEqual(self.n3.root(), self.n1)
        self.assertEqual(self.n4.root(), self.n1)
        self.assertEqual(self.n5.root(), self.n1)
        self.assertEqual(self.n6.root(), self.n1)
        self.assertEqual(self.n7.root(), self.n1)
        self.assertEqual(self.n8.root(), self.n1)
        self.assertEqual(self.n9.root(), self.n1)
        self.assertEqual(self.n10.root(), self.n1)
        self.assertEqual(self.n11.root(), self.n1)
        self.assertEqual(self.n12.root(), self.n12)
        self.assertEqual(self.n13.root(), self.n12)
        self.assertEqual(self.n14.root(), self.n12)
        self.assertEqual(self.n15.root(), self.n15)
        self.assertEqual(self.n16.root(), self.n15)
        self.assertEqual(self.n17.root(), self.n15)
        self.assertEqual(self.n18.root(), self.n18)
        self.assertEqual(self.n19.root(), self.n19)
        self.assertEqual(self.n20.root(), self.n20)
        self.assertEqual(self.n21.root(), self.n20)
        self.assertEqual(self.n22.root(), self.n20)
        self.assertEqual(self.n23.root(), self.n20)
        self.assertEqual(self.n24.root(), self.n20)
        self.assertEqual(self.n25.root(), self.n20)
        self.assertEqual(self.n26.root(), self.n20)
        self.assertEqual(self.n27.root(), self.n20)
        self.assertEqual(self.n28.root(), self.n20)
        self.assertEqual(self.n29.root(), self.n20)
        self.assertEqual(self.n30.root(), self.n20)
        self.assertEqual(self.n31.root(), self.n20)
        self.assertEqual(self.n32.root(), self.n20)

    def test_advanced_children(self):
        mn1 = HierarchicalModel.Node(self.n1)
        mn2 = HierarchicalModel.Node(self.n2)
        mn3 = HierarchicalModel.Node(self.n3)
        mn4 = HierarchicalModel.Node(self.n4)
        mn5 = HierarchicalModel.Node(self.n5)
        mn6 = HierarchicalModel.Node(self.n6)
        mn7 = HierarchicalModel.Node(self.n7)
        mn8 = HierarchicalModel.Node(self.n8)
        mn9 = HierarchicalModel.Node(self.n9)
        mn10 = HierarchicalModel.Node(self.n10)
        mn11 = HierarchicalModel.Node(self.n11)
        mn12 = HierarchicalModel.Node(self.n12)
        mn13 = HierarchicalModel.Node(self.n13)
        mn14 = HierarchicalModel.Node(self.n14)
        mn15 = HierarchicalModel.Node(self.n15)
        mn16 = HierarchicalModel.Node(self.n16)
        mn17 = HierarchicalModel.Node(self.n17)
        mn18 = HierarchicalModel.Node(self.n18)
        mn19 = HierarchicalModel.Node(self.n19)
        mn20 = HierarchicalModel.Node(self.n20)
        mn21 = HierarchicalModel.Node(self.n21)
        mn22 = HierarchicalModel.Node(self.n22)
        mn23 = HierarchicalModel.Node(self.n23)
        mn24 = HierarchicalModel.Node(self.n24)
        mn25 = HierarchicalModel.Node(self.n25)
        mn26 = HierarchicalModel.Node(self.n26)
        mn27 = HierarchicalModel.Node(self.n27)
        mn28 = HierarchicalModel.Node(self.n28)
        mn29 = HierarchicalModel.Node(self.n29)
        mn30 = HierarchicalModel.Node(self.n30)
        mn31 = HierarchicalModel.Node(self.n31)
        mn32 = HierarchicalModel.Node(self.n32)

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
        pass
