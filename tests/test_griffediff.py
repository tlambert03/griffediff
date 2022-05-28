from pathlib import Path
from types import FunctionType
from typing import Tuple

import pytest
from griffe.dataclasses import Module
from griffe.loader import GriffeLoader

from _api import old
from griffediff._compare import func_incompatibilities

FNAMES = [k for k, v in vars(old).items() if isinstance(v, FunctionType)]


@pytest.fixture
def old_new(monkeypatch) -> Tuple[Module, Module]:
    monkeypatch.syspath_prepend(Path(__file__).parent)
    loader = GriffeLoader()
    old = loader.load_module("_api.old")
    new = loader.load_module("_api.new")
    return old, new


@pytest.mark.parametrize("name", FNAMES)
def test_compare_function(name: str, old_new: Tuple[Module, Module]):
    old, new = old_new
    if name not in new.members:
        return
    new_func, old_func = new.members[name], old.members[name]
    reasons = func_incompatibilities(new_func, old_func)
    assert bool(reasons) != name.startswith("ok")
