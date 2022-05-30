import shutil
from pathlib import Path
from subprocess import run

import pytest

REPO_NAME = "my-repo"
REPO_SOURCE = Path(__file__).parent / "_repo"


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    """Fixture that creates a git repo with multiple tagged versions.

    For each directory in `tests/_repo/`

        - the contents of the directory will be copied into the temporary repo
        - all files will be added and commited
        - the commit will be tagged with the name of the directory
        - <repeat>

    To add to these tests (i.e. to simulate change over time), either modify one of
    the files in the existing `v0.1.0`, `v0.2.0` folders, or continue adding new
    version folders following the same pattern.
    """
    repo_path = tmp_path / REPO_NAME
    repo_path.mkdir()
    run(["git", "-C", str(repo_path), "init"])
    run(["git", "-C", str(repo_path), "config", "user.name", "Name"])
    run(["git", "-C", str(repo_path), "config", "user.email", "my@email.com"])
    for tagdir in REPO_SOURCE.iterdir():
        ver = tagdir.name
        _copy_contents(tagdir, repo_path)
        run(["git", "-C", str(repo_path), "add", "."])
        run(["git", "-C", str(repo_path), "commit", "-m", f"feat: {ver} stuff"])
        run(["git", "-C", str(repo_path), "tag", ver])
    return repo_path


def _copy_contents(src: Path, dst: Path) -> None:
    """Copy *contents* of src into dst."""
    dst.mkdir(exist_ok=True, parents=True)
    for src_path in src.iterdir():
        dst_path = dst / src_path.name
        if src_path.is_dir():
            _copy_contents(src_path, dst_path)
        else:
            shutil.copy(src_path, dst_path)
