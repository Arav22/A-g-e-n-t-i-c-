"""Minimal local pydantic-compatible shim for constrained environments."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, get_args, get_origin


class ValidationError(Exception):
    def __init__(self, errors: list[dict[str, Any]]):
        self._errors = errors
        super().__init__(str(errors))

    def errors(self) -> list[dict[str, Any]]:
        return self._errors


@dataclass
class _FieldInfo:
    default: Any = ...
    default_factory: Any = None
    min_length: int | None = None
    description: str | None = None


def Field(*, default: Any = ..., default_factory: Any = None, min_length: int | None = None, description: str | None = None):
    return _FieldInfo(default=default, default_factory=default_factory, min_length=min_length, description=description)


class ConfigDict(dict):
    pass


def _is_optional(tp: Any) -> bool:
    origin = get_origin(tp)
    if origin is None:
        return False
    return type(None) in get_args(tp)


class BaseModel:
    model_config = ConfigDict(extra="ignore")

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def model_validate(cls, payload: Any):
        if isinstance(payload, cls):
            return payload
        if not isinstance(payload, dict):
            raise ValidationError([{"loc": (), "msg": "Expected dictionary payload."}])

        annotations = getattr(cls, "__annotations__", {})
        values: dict[str, Any] = {}
        errors: list[dict[str, Any]] = []

        fields = {name: getattr(cls, name, ...) for name in annotations}

        extra_mode = getattr(cls, "model_config", {}).get("extra", "ignore")
        if extra_mode == "forbid":
            extra_keys = set(payload.keys()) - set(annotations.keys())
            for key in extra_keys:
                errors.append({"loc": (key,), "msg": "Extra fields not permitted."})

        for name, tp in annotations.items():
            spec = fields.get(name, ...)
            has_default = spec is not ...

            if name in payload:
                value = payload[name]
            elif isinstance(spec, _FieldInfo) and spec.default_factory is not None:
                value = spec.default_factory()
            elif isinstance(spec, _FieldInfo) and spec.default is not ...:
                value = deepcopy(spec.default)
            elif has_default and not isinstance(spec, _FieldInfo):
                value = deepcopy(spec)
            elif _is_optional(tp):
                value = None
            else:
                errors.append({"loc": (name,), "msg": "Field required."})
                continue

            if isinstance(spec, _FieldInfo) and spec.min_length is not None and isinstance(value, str):
                if len(value) < spec.min_length:
                    errors.append({"loc": (name,), "msg": f"String should have at least {spec.min_length} characters."})
                    continue

            values[name] = value

        if errors:
            raise ValidationError(errors)

        return cls(**values)
