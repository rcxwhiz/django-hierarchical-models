from typing import TypeVar

from django.test import TestCase

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

    def test_basic_create_child(self):
        parent = self.create(1)
        child = parent.create_child(num=2)
        self.assertIsNone(parent.parent())
        self.assertEqual(child.parent(), parent)

    def test_basic_remove_child(self):
        parent = self.create(1)
        child = self.create(2, parent=parent)
        parent.remove_child(child)
        self.assertIsNone(child.parent())

    def test_basic_ancestors(self):
        parent = self.create(1)
        child = self.create(2, parent=parent)
        self.assertListEqual(child.ancestors(), [parent])

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
