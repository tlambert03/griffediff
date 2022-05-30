import sys
from pathlib import Path
from types import FunctionType

import pytest
from griffe.dataclasses import Module
from griffe.loader import GriffeLoader

from griffediff._compare import func_incompatibilities, module_incompatibilities

_REPO = Path(__file__).parent / "_repo"

sys.path.insert(0, str(_REPO / "v0.1.0"))
import api as _old  # isort: skip  # noqa

FNAMES = [k for k, v in vars(_old).items() if isinstance(v, FunctionType)]
sys.path.pop(0)


@pytest.fixture
def old() -> Module:
    return GriffeLoader(search_paths=[_REPO / "v0.1.0"]).load_module("api")


@pytest.fixture
def new() -> Module:
    return GriffeLoader(search_paths=[_REPO / "v0.2.0"]).load_module("api")


@pytest.mark.parametrize("name", FNAMES)
def test_compare_function(name: str, old: Module, new: Module):
    if name in new.members:
        reasons = list(func_incompatibilities(old[name], new[name]))
        assert bool(reasons) != name.startswith("ok")


def test_compare_module(new: Module, old: Module):
    reasons = list(module_incompatibilities(old, new))
    assert reasons
