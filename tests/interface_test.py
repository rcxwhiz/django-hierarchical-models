import os

from django.conf import settings
from django.test import TestCase

from tests.interface_tester import HierarchicalModelInterfaceTester
from tests.models import ALMTestModel, NSMTestModel, PEMTestModel


class ALMInterfaceTest(HierarchicalModelInterfaceTester, TestCase):
    model_class = ALMTestModel


class NSMInterfaceTest(HierarchicalModelInterfaceTester, TestCase):
    model_class = NSMTestModel


class PEMInterfaceTest(HierarchicalModelInterfaceTester, TestCase):
    model_class = PEMTestModel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # don't want to skip tests if intended to use postgres
        if "POSTGRES_DB" not in os.environ:
            db_engine = settings.DATABASES["default"]["ENGINE"]

            if "sqlite" in db_engine or "oracle" in db_engine:
                self.__class__.__unittest_skip__ = True
                self.__class__.__unittest_skip_why__ = (
                    "PathEnumerationModel tests skipped due to sqlite or oracle db"
                    "engine."
                )
