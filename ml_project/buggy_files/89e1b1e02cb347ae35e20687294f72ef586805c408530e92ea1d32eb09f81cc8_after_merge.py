def _process_class(
    _cls: AnyType,
    init: bool,
    repr: bool,
    eq: bool,
    order: bool,
    unsafe_hash: bool,
    frozen: bool,
    config: Type['BaseConfig'],
) -> 'DataclassType':
    post_init_original = getattr(_cls, '__post_init__', None)
    post_init_post_parse = getattr(_cls, '__post_init_post_parse__', None)
    if post_init_original and post_init_original.__name__ == '_pydantic_post_init':
        post_init_original = None

    def _pydantic_post_init(self: 'DataclassType', *initvars: Any) -> None:
        if post_init_original is not None:
            post_init_original(self, *initvars)
        d = validate_model(self.__pydantic_model__, self.__dict__, cls=self.__class__)[0]
        object.__setattr__(self, '__dict__', d)
        object.__setattr__(self, '__initialised__', True)
        if post_init_post_parse is not None:
            post_init_post_parse(self)

    _cls.__post_init__ = _pydantic_post_init
    cls = dataclasses._process_class(_cls, init, repr, eq, order, unsafe_hash, frozen)  # type: ignore

    fields: Dict[str, Any] = {
        field.name: (field.type, field.default if field.default != dataclasses.MISSING else Required)
        for field in dataclasses.fields(cls)
    }

    validators = gather_validators(cls)
    cls.__pydantic_model__ = create_model(
        cls.__name__, __config__=config, __module__=_cls.__module__, __validators__=validators, **fields
    )

    cls.__initialised__ = False
    cls.__validate__ = classmethod(_validate_dataclass)
    cls.__get_validators__ = classmethod(_get_validators)

    if cls.__pydantic_model__.__config__.validate_assignment and not frozen:
        cls.__setattr__ = setattr_validate_assignment

    return cls