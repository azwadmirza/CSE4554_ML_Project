def _process_class(_cls, init, repr, eq, order, unsafe_hash, frozen, validate_assignment):
    post_init_original = getattr(_cls, '__post_init__', None)
    _cls.__post_init__ = post_init
    cls = dataclasses._process_class(_cls, init, repr, eq, order, unsafe_hash, frozen)

    fields = {name: (field.type, field.default) for name, field in cls.__dataclass_fields__.items()}
    cls.__post_init_original__ = post_init_original
    cls.__pydantic_model__ = create_model(cls.__name__, **fields)
    cls.__initialised__ = False

    if validate_assignment and not frozen:
        cls.__setattr__ = setattr_validate_assignment
    return cls