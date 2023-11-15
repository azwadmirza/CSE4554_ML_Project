def make_dataclass_validator(_cls: Type[Any], config: Type['BaseConfig']) -> 'CallableGenerator':
    """
    Create a pydantic.dataclass from a builtin dataclass to add type validation
    and yield the validators
    """
    cls = dataclass(_cls, config=config)
    yield from _get_validators(cls)