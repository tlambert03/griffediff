from typing import Iterator

from griffe.dataclasses import Module

from ._breakage import Breakage
from ._members import member_incompatibilities


def module_incompatibilities(
    old_mod: Module,
    new_mod: Module,
    ignore_private: bool = True,
) -> Iterator[Breakage]:
    yield from member_incompatibilities(old_mod, new_mod, ignore_private=ignore_private)
