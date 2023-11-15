def _process_class(
    _cls: Type[Any],
    init: bool,
    repr: bool,
    eq: bool,
    order: bool,
    unsafe_hash: bool,
    frozen: bool,
    config: Optional[Type[Any]],
) -> Type['Dataclass']:
    import dataclasses

    post_init_original = getattr(_cls, '__post_init__', None)
    if post_init_original and post_init_original.__name__ == '_pydantic_post_init':
        post_init_original = None
    if not post_init_original:
        post_init_original = getattr(_cls, '__post_init_original__', None)

    post_init_post_parse = getattr(_cls, '__post_init_post_parse__', None)

    def _pydantic_post_init(self: 'Dataclass', *initvars: Any) -> None:
        if post_init_original is not None:
            post_init_original(self, *initvars)
        d, _, validation_error = validate_model(self.__pydantic_model__, self.__dict__, cls=self.__class__)
        if validation_error:
            raise validation_error
        object.__setattr__(self, '__dict__', d)
        object.__setattr__(self, '__initialised__', True)
        if post_init_post_parse is not None:
            post_init_post_parse(self, *initvars)

    # If the class is already a dataclass, __post_init__ will not be called automatically
    # so no validation will be added.
    # We hence create dynamically a new dataclass:
    # ```
    # @dataclasses.dataclass
    # class NewClass(_cls):
    #   __post_init__ = _pydantic_post_init
    # ```
    # with the exact same fields as the base dataclass
    if is_builtin_dataclass(_cls):
        _cls = type(
            _cls.__name__, (_cls,), {'__annotations__': _cls.__annotations__, '__post_init__': _pydantic_post_init}
        )
    else:
        _cls.__post_init__ = _pydantic_post_init
    cls: Type['Dataclass'] = dataclasses.dataclass(  # type: ignore
        _cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash, frozen=frozen
    )
    cls.__processed__ = ClassAttribute('__processed__', True)

    fields: Dict[str, Any] = {}
    for field in dataclasses.fields(cls):

        if field.default != dataclasses.MISSING:
            field_value = field.default
        # mypy issue 7020 and 708
        elif field.default_factory != dataclasses.MISSING:  # type: ignore
            field_value = field.default_factory()  # type: ignore
        else:
            field_value = Required

        fields[field.name] = (field.type, field_value)

    validators = gather_all_validators(cls)
    cls.__pydantic_model__ = create_model(
        cls.__name__, __config__=config, __module__=_cls.__module__, __validators__=validators, **fields
    )

    cls.__initialised__ = False
    cls.__validate__ = classmethod(_validate_dataclass)  # type: ignore[assignment]
    cls.__get_validators__ = classmethod(_get_validators)  # type: ignore[assignment]
    if post_init_original:
        cls.__post_init_original__ = post_init_original

    if cls.__pydantic_model__.__config__.validate_assignment and not frozen:
        cls.__setattr__ = setattr_validate_assignment  # type: ignore[assignment]

    return cls