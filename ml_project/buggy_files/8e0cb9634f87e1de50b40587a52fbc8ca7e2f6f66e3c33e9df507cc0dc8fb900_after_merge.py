def make_dataclass_validator(_cls: Type[Any], config: Type['BaseConfig']) -> 'CallableGenerator':
    """
    Create a pydantic.dataclass from a builtin dataclass to add type validation
    and yield the validators
    It retrieves the parameters of the dataclass and forwards them to the newly created dataclass
    """
    dataclass_params = _cls.__dataclass_params__
    stdlib_dataclass_parameters = {param: getattr(dataclass_params, param) for param in dataclass_params.__slots__}
    cls = dataclass(_cls, config=config, **stdlib_dataclass_parameters)
    yield from _get_validators(cls)