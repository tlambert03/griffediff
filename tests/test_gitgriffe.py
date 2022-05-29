from griffediff._git import git_compare


def test_compare():
    aa = git_compare("v0.3.0", "v0.3.4", "psygnal", "/Users/talley/python/psygnal")
    assert list(aa)
