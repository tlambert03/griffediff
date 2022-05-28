from typing import Iterator, cast

from griffe.dataclasses import Attribute, Class, Function, Module, Object

from ._attribute import attr_incompatibilities
from ._breakage import Breakage, BreakageKind
from ._class import class_incompatibilities
from ._function import func_incompatibilities


def obj_incompatibilities(
    old_obj: Object, new_obj: Object, ignore_private: bool = True
) -> Iterator[Breakage]:

    for name, member in old_obj.members.items():
        if not isinstance(member, Object) or (ignore_private and name.startswith("_")):
            continue
        if name in new_obj.members:
            newmem = new_obj.members[name]
            if newmem.kind != member.kind:
                yield Breakage(BreakageKind.NAME_TYPE_CHANGED, member)
            elif isinstance(member, Module):
                yield from obj_incompatibilities(member, cast(Module, newmem))
            elif isinstance(member, Class):
                yield from class_incompatibilities(member, cast(Class, newmem))
            elif isinstance(member, Function):
                yield from func_incompatibilities(member, cast(Function, newmem))
            elif isinstance(member, Attribute):
                yield from attr_incompatibilities(member, cast(Attribute, newmem))
        else:
            yield Breakage(BreakageKind.NAME_REMOVED, member)
