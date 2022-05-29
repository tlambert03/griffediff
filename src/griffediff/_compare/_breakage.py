import enum
from typing import Optional, Union

from griffe.dataclasses import Alias, Class, Function, Object, Parameter
from griffe.exceptions import AliasResolutionError


class BreakageKind(enum.Enum):
    PARAMETER_REMOVED = "Parameter removed"
    PARAMETER_NOW_REQUIRED = "Parameter now required"
    PARAMETER_MOVED = "Positional parameter moved"
    PARAMETER_KIND_CHANGED = "Positional parameter changed to keyword parameter"
    PARAMETER_DEFAULT_CHANGED = "Positional parameter changed to keyword parameter"
    PARAMETER_NEW_ADDED = "New required parameter added"
    INCOMPATIBLE_RETURN = "Return types are incompatible"
    NAME_REMOVED = "Public name has been removed or changed."
    NAME_TYPE_CHANGED = "Public name points to a different type of object."
    ATTRIBUTE_TYPE_CHANGED = "New attribute type is incompatible"
    ATTRIBUTE_VALUE_CHANGED = "Attribute value has changed"
    CLASS_BASE_REMOVED = "Removed base class"


class Breakage:
    def __init__(
        self, kind: BreakageKind, obj: Union[Object, Alias], reason: str = ""
    ) -> None:
        self.kind = kind
        self.obj = obj
        self.reason = reason

    def __str__(self) -> str:
        return f"{self.kind.value}: {self._safe_path}"

    def __repr__(self) -> str:
        return f"<{self.kind.name}: {self._safe_path}>"

    @property
    def _safe_path(self) -> str:
        try:
            return str(self.obj.canonical_path)
        except AliasResolutionError:
            return getattr(self.obj, "target_path", "")


class ParameterBreakage(Breakage):
    def __init__(
        self,
        kind: BreakageKind,
        obj: Object,
        param: Parameter,
        new_param: Optional[Parameter] = None,
        reason: str = "",
    ) -> None:
        super().__init__(kind=kind, obj=obj, reason=reason)
        self.param = param
        self.new_param = new_param

    def __str__(self) -> str:
        return f"{super().__str__()} ({self.param.name!r})"


class ReturnBreakage(Breakage):
    def __init__(self, obj: Function, new_func: Function) -> None:
        super().__init__(BreakageKind.INCOMPATIBLE_RETURN, obj)
        self.new_func = new_func


class ClassBreakage(Breakage):
    def __init__(
        self,
        kind: BreakageKind,
        old_cls: Class,
        new_cls: Optional[Class],
        reason: str = "",
    ) -> None:
        super().__init__(kind, old_cls, reason)
        self.new_cls = new_cls
