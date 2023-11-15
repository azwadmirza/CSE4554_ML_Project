def make_dataclass_validator(_cls: Type[Any], **kwargs: Any) -> 'CallableGenerator':
    """
    Create a pydantic.dataclass from a builtin dataclass to add type validation
    and yield the validators
    """
    cls = dataclass(_cls, **kwargs)
    yield from _get_validators(cls)