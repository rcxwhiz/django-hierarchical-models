import importlib
from typing import TypeVar

from django.conf import settings

from .hierarchical_model import HierarchicalModel

T = TypeVar("T", bound=HierarchicalModel)
DefaultHierarchicalModel: T

settings_label = "DEFAULT_HIERARCHICAL_MODEL"
default_class_name = "AdjacencyListModel"
valid_classes = {"AdjacencyListModel": "django_hierarchical_models.models.alm"}

class_name = getattr(settings, settings_label, default_class_name)
if class_name not in valid_classes:
    raise TypeError(f"{class_name} not a valid HierarchicalModel")

model_module = importlib.import_module(valid_classes[class_name])
DefaultHierarchicalModel = getattr(model_module, class_name)
