import builtins
import importlib
from typing import Any, Union, get_origin

from griffe.expressions import Expression, Name

BUILTIN_NAMES = dir(builtins)


def is_subtype(typ: Any, typ_or_tuple: Any) -> bool:
    """Return whether 'typ' is derived from another type or is the same type.

    would like to supports PEP 484 style types from typing module.
    Would prefer to use https://github.com/Stewori/pytypes ... but it is broken for
    py3.10, and may not be receiving updates:
    https://github.com/Stewori/pytypes/issues/116
    """
    if isinstance(typ_or_tuple, tuple):
        return any(is_subtype(typ, x) for x in typ_or_tuple)

    if isinstance(typ, (str, Name, Expression)):
        typ = resolve(typ)
    if isinstance(typ_or_tuple, (str, Name, Expression)):
        typ_or_tuple = resolve(typ_or_tuple)

    # TODO: Unions, Generic ... so many things
    ao = typ if isinstance(typ, type) else get_origin(typ)
    bo = typ_or_tuple if isinstance(typ_or_tuple, type) else get_origin(typ_or_tuple)
    if typ is None or bo is None:
        return False
    if typ is bo:
        return True
    return isinstance(ao, type) and isinstance(bo, type) and issubclass(ao, bo)


def resolve(annotation: Union[str, Name, Expression]) -> object:
    """Resolve `annotation` to python object."""

    if isinstance(annotation, str):
        name: str = annotation
    elif isinstance(annotation, Name):
        name = annotation.full
    elif isinstance(annotation, Expression):
        raise NotImplementedError()
    else:
        raise TypeError("annotation must be a string, Name, or Expression")

    if name in BUILTIN_NAMES:
        return getattr(builtins, name)

    module_name, class_name = name.rsplit(".", 1)
    somemodule = importlib.import_module(module_name)
    return getattr(somemodule, class_name)
