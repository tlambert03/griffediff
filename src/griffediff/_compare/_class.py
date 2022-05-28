from typing import Iterable

from griffe.dataclasses import Class

from ._breakage import Breakage


def class_incompatibilities(old_cls: Class, new_cls: Class) -> Iterable[Breakage]:
    yield from ()
    return
