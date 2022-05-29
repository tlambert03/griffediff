from ._attribute import attr_incompatibilities
from ._breakage import Breakage, BreakageKind
from ._class import class_incompatibilities
from ._function import func_incompatibilities
from ._module import module_incompatibilities

__all__ = [
    "Breakage",
    "BreakageKind",
    "attr_incompatibilities",
    "class_incompatibilities",
    "func_incompatibilities",
    "module_incompatibilities",
]
