def setattr_validate_assignment(self: 'DataclassType', name: str, value: Any) -> None:
    if self.__initialised__:
        d = dict(self.__dict__)
        d.pop(name)
        value, error_ = self.__pydantic_model__.__fields__[name].validate(value, d, loc=name, cls=self.__class__)
        if error_:
            raise ValidationError([error_], type(self))

    object.__setattr__(self, name, value)