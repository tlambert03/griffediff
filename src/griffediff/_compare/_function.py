import contextlib
from typing import Iterator, Union

from griffe.dataclasses import Function, Parameter, ParameterKind
from griffe.expressions import Expression, Name

from .._types import is_subtype
from ._breakage import Breakage, BreakageKind, ParameterBreakage, ReturnBreakage

POSITIONAL = {ParameterKind.positional_only, ParameterKind.positional_or_keyword}


# TODO: decorators!
def func_incompatibilities(
    old_func: Function, new_func: Function
) -> Iterator[Breakage]:
    with contextlib.suppress(ValueError):
        # could remove this
        same = new_func.as_dict() == old_func.as_dict()
        if same:
            return

    new_param_names = [p.name for p in new_func.parameters]

    for i, param in enumerate(old_func.parameters):
        if param.name not in new_func.parameters:
            yield ParameterBreakage(BreakageKind.PARAMETER_REMOVED, old_func, param)
            continue

        new_param = new_func.parameters[param.name]
        if _is_param_required(new_param) and not _is_param_required(param):
            yield ParameterBreakage(
                BreakageKind.PARAMETER_NOW_REQUIRED, old_func, param, new_param
            )

        if param.kind in POSITIONAL:
            if new_param_names.index(param.name) != i:
                yield ParameterBreakage(
                    BreakageKind.PARAMETER_MOVED, old_func, param, new_param
                )
            if new_param.kind not in POSITIONAL:
                yield ParameterBreakage(
                    BreakageKind.PARAMETER_KIND_CHANGED, old_func, param, new_param
                )

        b = ParameterBreakage(
            BreakageKind.PARAMETER_DEFAULT_CHANGED, old_func, param, new_param
        )
        try:
            if param.default != new_param.default:
                yield b
        except Exception:  # equality checks sometimes fail, e.g. numpy arrays
            # TODO: emitting breakage on a failed comparison could be a preference
            yield b

    for new_param in new_func.parameters:
        if new_param.name not in old_func.parameters and _is_param_required(new_param):
            yield ParameterBreakage(
                BreakageKind.PARAMETER_NEW_ADDED, old_func, new_param
            )

    if not _returns_are_compatible(old_func, new_func):
        yield ReturnBreakage(old_func, new_func)


def _is_param_required(param: Parameter) -> bool:
    return param.kind in POSITIONAL and param.default is None


Return = Union[str, Name, Expression, None]


def _returns_are_compatible(old_func: Function, new_func: Function) -> bool:
    if old_func.returns is None:
        return True
    if new_func.returns is None:
        # TODO: it should be configurable to allow/disallow removing a return type
        return False

    with contextlib.suppress(AttributeError):
        if new_func.returns == old_func.returns:
            return True
    try:
        return is_subtype(new_func.returns, old_func.returns)
    except Exception:
        return True
