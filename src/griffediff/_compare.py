import contextlib
from typing import Iterator, NewType, Union

from griffe.dataclasses import Function, Parameter, ParameterKind
from griffe.expressions import Expression, Name

from ._types import is_subtype

Reason = NewType("Reason", str)

POSITIONAL = {ParameterKind.positional_only, ParameterKind.positional_or_keyword}


def func_incompatibilities(new_func: Function, old_func: Function) -> Iterator[Reason]:
    with contextlib.suppress(ValueError):
        same = new_func.as_dict() == old_func.as_dict()
        if same:
            return

    new_param_names = [p.name for p in new_func.parameters]

    for i, param in enumerate(old_func.parameters):
        if param.name not in new_func.parameters:
            yield Reason(f"Parameter removed: {param.name!r}")
            continue

        new_param = new_func.parameters[param.name]
        if _is_param_required(new_param) and not _is_param_required(param):
            yield Reason(f"Parameter now required: {param.name!r}")

        if param.kind in POSITIONAL:
            if (new_i := new_param_names.index(param.name)) != i:
                yield Reason(
                    f"Positional parameter {param.name!r} has moved from "
                    f"position {i} to {new_i}."
                )
            if new_param.kind not in POSITIONAL:
                newtype = new_param.kind.value if new_param.kind else "no type"
                yield Reason(
                    f"{param.kind.value} parameter changed to {newtype}: {param.name!r}"
                )

        new_default_msg = (
            f"Parameter {param.name!r} default changed from {param.default!r} "
            f"to {new_param.default!r}"
        )
        try:
            if param.default != new_param.default:
                yield Reason(new_default_msg)
        except Exception:  # equality checks sometimes fail, e.g. numpy arrays
            yield Reason(new_default_msg)

    for new_param in new_func.parameters:
        if new_param.name not in old_func.parameters and _is_param_required(new_param):
            yield Reason(f"Required parameter added: {new_param.name!r}")

    if not _returns_are_compatible(old_func.returns, new_func.returns):
        yield Reason("Return type is incompatible")


def _is_param_required(param: Parameter) -> bool:
    return param.kind in POSITIONAL and param.default is None


Return = Union[str, Name, Expression, None]


def _returns_are_compatible(old_return: Return, new_return: Return) -> bool:
    if old_return is None:
        return True
    if new_return is None:
        # TODO: it should be configurable to allow/disallow removing a return type
        return False
    return is_subtype(new_return, old_return)
