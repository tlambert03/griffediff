import builtins
from typing import Any, Optional, Union, get_origin, get_type_hints

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


class _Ann:
    _KEY = "__obj"

    def __init__(self, obj: str) -> None:
        self.__annotations__ = {self._KEY: obj}

    def resolve(
        self,
        globalns: Optional[dict] = None,
        localns: Optional[dict] = None,
        include_extras: bool = False,
    ) -> Any:
        import typing

        localns = localns or {}
        localns.update({**vars(typing), "typing": typing})
        return get_type_hints(self, globalns, localns, include_extras).get(self._KEY)


def _resolve_ref(
    obj: str,
    globalns: Optional[dict] = None,
    localns: Optional[dict] = None,
    include_extras: bool = False,
) -> Any:
    if obj in BUILTIN_NAMES:
        return getattr(builtins, obj)
    return _Ann(obj).resolve(globalns, localns, include_extras)


def resolve(annotation: Union[str, Name, Expression]) -> Any:
    """Resolve `annotation` to python object."""

    if isinstance(annotation, str):
        name: str = annotation
    elif isinstance(annotation, Name):
        name = annotation.full
    elif isinstance(annotation, Expression):
        name = annotation[0].full
        # TODO... more to it
    else:
        raise TypeError("annotation must be a string, Name, or Expression")

    return _resolve_ref(name)
