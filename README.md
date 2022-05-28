# griffediff

[![License](https://img.shields.io/pypi/l/griffediff.svg?color=green)](https://github.com/tlambert03/griffediff/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/griffediff.svg?color=green)](https://pypi.org/project/griffediff)
[![Python Version](https://img.shields.io/pypi/pyversions/griffediff.svg?color=green)](https://python.org)
[![CI](https://github.com/tlambert03/griffediff/actions/workflows/ci.yml/badge.svg)](https://github.com/tlambert03/griffediff/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tlambert03/griffediff/branch/main/graph/badge.svg)](https://codecov.io/gh/tlambert03/griffediff)

API comparison and breaking-change detection using [griffe](https://github.com/mkdocstrings/griffe).

***Experimental!***

See also: https://github.com/Carreau/frappuccino

----

Examples of allowed non-breaking API changes:

```python
def add_optional_param(a):
def add_optional_param(a, c=2):

def change_keywordonly_position(a, *, b=1, c=2):
def change_keywordonly_position(a, *, c=2, b=1):

def change_return_type() -> Sequence:
def change_return_type() -> list:
```

Examples of breaking API changes detected

```python
def remove_param(a, b): #
def remove_param(a):

def change_param_name(a, b):
def change_param_name(a, c):

def change_param_default(a, b=1):
def change_param_default(a, b=2):

def add_required_param(a):
def add_required_param(a, b):

def change_kwarg_to_positional(a, b=1):
def change_kwarg_to_positional(a, b):

def change_position_of_positional(a, b):
def change_position_of_positional(b, a):

def change_keyword_position(a, b=1, c=2):
def change_keyword_position(a, c=2, b=1):

def change_pos_to_keyword_only(a, b=1):
def change_pos_to_keyword_only(a, *, b=1):

def change_return_type_incompatible() -> list:
def change_return_type_incompatible() -> Sequence:

def removed_public_function():
def _removed_public_function():
```
