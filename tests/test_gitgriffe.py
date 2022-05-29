import os
import shutil
from pathlib import Path

import pytest

from griffediff._git import git_compare

API_PKG = Path(__file__).parent / "api-pkg"


@pytest.fixture
def api_pkg(tmp_path: Path):
    new_dir = shutil.copytree(API_PKG, tmp_path / "api-pkg")
    os.rename((new_dir / "_git"), (new_dir / ".git"))
    return new_dir


def test_git_compare(api_pkg: Path):
    aa = list(git_compare("old", "new", "api", api_pkg))
    assert len(aa) > 16
    msgs = {str(i) for i in aa}
    assert "Parameter removed: api.change_param_name ('b')" in msgs
    assert "New required parameter added: api.change_param_name ('c')" in msgs
    assert "Parameter now required: api.change_kwarg_to_pos ('b')" in msgs
