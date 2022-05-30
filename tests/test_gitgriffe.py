from pathlib import Path

from griffediff._git import git_compare

MOD = "api"


def test_git_compare(git_repo: Path):
    aa = list(git_compare("v0.1.0", "v0.2.0", MOD, git_repo))
    assert len(aa) > 16
    msgs = {str(i) for i in aa}
    assert f"Parameter removed: {MOD}.change_param_name ('b')" in msgs
    assert f"New required parameter added: {MOD}.change_param_name ('c')" in msgs
    assert f"Parameter now required: {MOD}.change_kwarg_to_pos ('b')" in msgs
