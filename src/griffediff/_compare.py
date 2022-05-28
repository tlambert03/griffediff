import builtins
import contextlib
import importlib
from typing import Any, List, NewType, Union, cast, get_origin

from griffe.dataclasses import Function, Parameter, ParameterKind
from griffe.expressions import Expression, Name

Reason = NewType("Reason", str)
Return = Union[str, Name, Expression, None]

POSITIONAL = {ParameterKind.positional_only, ParameterKind.positional_or_keyword}
BUILTIN_NAMES = dir(builtins)


def _is_required(param: Parameter) -> bool:
    return param.kind in POSITIONAL and param.default is None


def is_subtype(typ: Any, typ_or_tuple: Any) -> bool:
    """Return whether 'typ' is derived from another type or is the same type.

    would like to supports PEP 484 style types from typing module.
    Would prefer to use https://github.com/Stewori/pytypes ... but it is broken for
    py3.10, and may not be receiving updates:
    https://github.com/Stewori/pytypes/issues/116
    """
    if isinstance(typ_or_tuple, tuple):
        return any(is_subtype(typ, x) for x in typ_or_tuple)

    # TODO: Unions, Generic ... so many things
    ao = typ if isinstance(typ, type) else get_origin(typ)
    bo = typ_or_tuple if isinstance(typ_or_tuple, type) else get_origin(typ_or_tuple)
    if typ is None or bo is None:
        return False
    if typ is bo:
        return True
    return isinstance(ao, type) and isinstance(bo, type) and issubclass(ao, bo)


def _resolve(annotation: Union[str, Name, Expression]) -> object:

    name: str = annotation
    if isinstance(annotation, Name):
        name = annotation.full
    elif isinstance(annotation, Expression):
        raise NotImplementedError()

    if name in BUILTIN_NAMES:
        return getattr(builtins, name)

    module_name, class_name = name.rsplit(".", 1)
    somemodule = importlib.import_module(module_name)
    return getattr(somemodule, class_name)


def _returns_are_compatible(old_return: Return, new_return: Return) -> bool:
    if old_return is None:
        return True
    if new_return is None:
        # TODO: it should be configurable to allow/disallow removing a return type
        return False

    old = _resolve(old_return)
    new = _resolve(new_return)
    return is_subtype(new, old)


def func_incompatibilities(new_func: Function, old_func: Function) -> List[Reason]:
    with contextlib.suppress(ValueError):
        same = new_func.as_dict() == old_func.as_dict()
        if same:
            return []

    reasons: List[str] = []
    if new_func.name != old_func.name:
        reasons.append("Name changed")

    old_params = old_func.parameters
    new_params = new_func.parameters
    new_param_names = [p.name for p in new_params]

    for i, param in enumerate(old_params):
        if param.name not in new_params:
            reasons.append(f"Parameter removed: {param.name!r}")
            continue
        new_param = new_params[param.name]
        if _is_required(new_param) and not _is_required(param):
            reasons.append(f"Parameter now required: {param.name!r}")
        if param.kind in POSITIONAL:
            if (new_i := new_param_names.index(param.name)) != i:
                reasons.append(
                    f"Positional parameter {param.name!r} has moved from "
                    f"position {i} to {new_i}."
                )
            if new_param.kind not in POSITIONAL:
                newtype = new_param.kind.value if new_param.kind else "no type"
                reasons.append(
                    f"{param.kind.value} parameter changed to {newtype}: {param.name!r}"
                )

        new_default_msg = (
            f"Parameter {param.name!r} default changed from {param.default!r} "
            f"to {new_param.default!r}"
        )
        try:
            if param.default != new_param.default:
                reasons.append(new_default_msg)
        except Exception:  # equality checks sometimes fail, e.g. numpy arrays
            reasons.append(new_default_msg)

    reasons.extend(
        f"Required parameter added: {new_param.name!r}"
        for new_param in new_params
        if new_param.name not in old_params and _is_required(new_param)
    )

    if not _returns_are_compatible(old_func.returns, new_func.returns):
        reasons.append("Return type is incompatible")

    return cast(List[Reason], reasons)
