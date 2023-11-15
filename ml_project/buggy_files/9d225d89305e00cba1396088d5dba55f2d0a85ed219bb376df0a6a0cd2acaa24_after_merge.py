def find_validators(type_: AnyType, arbitrary_types_allowed: bool = False) -> List[AnyCallable]:
    if type_ is Any or type(type_) in (ForwardRef, TypeVar):
        return []
    if type_ is Pattern:
        return pattern_validators
    if is_callable_type(type_):
        return [callable_validator]

    supertype = _find_supertype(type_)
    if supertype is not None:
        type_ = supertype

    for val_type, validators in _VALIDATORS:
        try:
            if issubclass(type_, val_type):
                return validators
        except TypeError as e:
            raise RuntimeError(f'error checking inheritance of {type_!r} (type: {display_as_type(type_)})') from e

    if arbitrary_types_allowed:
        return [make_arbitrary_type_validator(type_)]
    else:
        raise RuntimeError(f'no validator found for {type_}')