from pathlib import Path
from types import FunctionType

import pytest
from griffe.dataclasses import Module
from griffe.loader import GriffeLoader

from _api import old
from griffediff._compare import func_incompatibilities, module_incompatibilities

FNAMES = [k for k, v in vars(old).items() if isinstance(v, FunctionType)]


@pytest.fixture
def api(monkeypatch) -> Module:
    monkeypatch.syspath_prepend(Path(__file__).parent)
    loader = GriffeLoader()
    return loader.load_module("_api")


@pytest.fixture
def old(api) -> Module:
    return api["old"]


@pytest.fixture
def new(api) -> Module:
    return api["new"]


@pytest.mark.parametrize("name", FNAMES)
def test_compare_function(name: str, old: Module, new: Module):
    if name in new.members:
        reasons = list(func_incompatibilities(old[name], new[name]))
        assert bool(reasons) != name.startswith("ok")


def test_compare_module(new: Module, old: Module):
    reasons = list(module_incompatibilities(old, new))
    assert reasons
