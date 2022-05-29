from typing import Iterator, Union, cast

from griffe.dataclasses import Alias, Attribute, Class, Function, Module, Object

from ._breakage import Breakage, BreakageKind


def member_incompatibilities(
    old_obj: Union[Object, Alias],
    new_obj: Union[Object, Alias],
    ignore_private: bool = True,
) -> Iterator[Breakage]:
    from ._attribute import attr_incompatibilities
    from ._class import class_incompatibilities
    from ._function import func_incompatibilities

    for name, member in old_obj.members.items():
        if ignore_private and name.startswith("_"):
            continue
        if name in new_obj.members:
            newmem = new_obj.members[name]
            if newmem.kind != member.kind:
                yield Breakage(BreakageKind.NAME_TYPE_CHANGED, member)

            # FIXME: probably wrong
            if isinstance(member, Alias):
                try:
                    if member.target.package.name == old_obj.package.name:
                        member = member.target
                    else:
                        continue
                except Exception:
                    continue
            if isinstance(member, Module):
                yield from member_incompatibilities(
                    member, cast(Module, newmem), ignore_private=ignore_private
                )
            elif isinstance(member, Class):
                yield from class_incompatibilities(
                    member, cast(Class, newmem), ignore_private=ignore_private
                )
            elif isinstance(member, Function):
                yield from func_incompatibilities(member, cast(Function, newmem))
            elif isinstance(member, Attribute):
                yield from attr_incompatibilities(member, cast(Attribute, newmem))
        elif member.is_implicitely_exported or member.is_explicitely_exported:
            yield Breakage(BreakageKind.NAME_REMOVED, member)
