def find_validators(  # noqa: C901 (ignore complexity)
    type_: Type[Any], config: Type['BaseConfig']
) -> Generator[AnyCallable, None, None]:
    from .dataclasses import is_builtin_dataclass, make_dataclass_validator

    if type_ is Any:
        return
    type_type = type_.__class__
    if type_type == ForwardRef or type_type == TypeVar:
        return
    if type_ is Pattern:
        yield pattern_validator
        return
    if type_ is Hashable:
        yield hashable_validator
        return
    if is_callable_type(type_):
        yield callable_validator
        return
    if is_literal_type(type_):
        yield make_literal_validator(type_)
        return
    if is_builtin_dataclass(type_):
        yield from make_dataclass_validator(type_)
        return
    if type_ is Enum:
        yield enum_validator
        return
    if type_ is IntEnum:
        yield int_enum_validator
        return

    class_ = get_class(type_)
    if class_ is not None:
        if isinstance(class_, type):
            yield make_class_validator(class_)
        else:
            yield any_class_validator
        return

    for val_type, validators in _VALIDATORS:
        try:
            if issubclass(type_, val_type):
                for v in validators:
                    if isinstance(v, IfConfig):
                        if v.check(config):
                            yield v.validator
                    else:
                        yield v
                return
        except TypeError:
            raise RuntimeError(f'error checking inheritance of {type_!r} (type: {display_as_type(type_)})')

    if config.arbitrary_types_allowed:
        yield make_arbitrary_type_validator(type_)
    else:
        raise RuntimeError(f'no validator found for {type_}, see `arbitrary_types_allowed` in Config')