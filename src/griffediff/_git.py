import os
from contextlib import contextmanager
from subprocess import DEVNULL, CalledProcessError, check_output, run
from tempfile import TemporaryDirectory
from typing import Iterator
from uuid import uuid1

from griffe.dataclasses import Module
from griffe.loader import GriffeLoader

from ._compare import Breakage, module_incompatibilities


def _assert_git_repo(repo: str) -> None:
    try:
        check_output(
            ["git", "-C", repo, "rev-parse", "--is-inside-work-tree"], stderr=DEVNULL
        )
    except CalledProcessError as e:
        raise ValueError(f"not a git repository: {repo!r}") from e


@contextmanager
def tmp_worktree(commit: str = "HEAD", repo: str = ".") -> Iterator[str]:
    _assert_git_repo(repo)
    with TemporaryDirectory() as td:
        _name = str(uuid1())
        target = os.path.join(td, _name)
        run(
            ["git", "-C", repo, "worktree", "add", "-b", _name, target, commit],
            stdout=DEVNULL,
            stderr=DEVNULL,
        )
        try:
            yield target
        finally:
            run(["git", "-C", repo, "worktree", "remove", _name], stdout=DEVNULL)
            run(["git", "-C", repo, "worktree", "prune"], stdout=DEVNULL)
            run(["git", "-C", repo, "branch", "-d", _name], stdout=DEVNULL)


def git_module(module_name: str, commit: str = "HEAD", repo: str = ".") -> Module:
    with tmp_worktree(commit, repo) as wrk:
        loader = GriffeLoader(search_paths=[wrk])
        return loader.load_module(module_name)


def git_compare(
    old_commit: str, new_commit: str, module_name: str, repo: str = "."
) -> Iterator[Breakage]:
    mod_old = git_module(module_name, old_commit, repo)
    mod_new = git_module(module_name, new_commit, repo)
    yield from module_incompatibilities(mod_old, mod_new)
