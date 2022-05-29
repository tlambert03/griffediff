from typing import Iterable

from griffe.dataclasses import Class

from ._breakage import Breakage, BreakageKind, ClassBreakage
from ._members import member_incompatibilities


# TODO: decorators!
def class_incompatibilities(
    old_cls: Class, new_cls: Class, ignore_private: bool = True
) -> Iterable[Breakage]:

    yield from ()
    if new_cls.bases != old_cls.bases:
        if len(new_cls.bases) < len(old_cls.bases):
            yield ClassBreakage(BreakageKind.CLASS_BASE_REMOVED, old_cls, new_cls)
        else:
            # TODO: check mro
            ...
    yield from member_incompatibilities(old_cls, new_cls, ignore_private=ignore_private)
