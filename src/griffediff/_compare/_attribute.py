from typing import Iterable

from griffe.dataclasses import Attribute

from .._types import is_subtype
from ._breakage import Breakage, BreakageKind


def attr_incompatibilities(
    old_attr: Attribute, new_attr: Attribute
) -> Iterable[Breakage]:
    if (
        old_attr.annotation is not None
        and new_attr.annotation is not None
        and not is_subtype(new_attr.annotation, old_attr.annotation)
    ):
        yield Breakage(BreakageKind.ATTRIBUTE_TYPE_CHANGED, old_attr)
    if old_attr.value != new_attr.value:
        yield Breakage(BreakageKind.ATTRIBUTE_VALUE_CHANGED, old_attr)
