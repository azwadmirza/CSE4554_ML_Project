    def validate(cls: Type['Model'], value: Any) -> 'Model':
        if isinstance(value, cls):
            return value.copy() if cls.__config__.copy_on_model_validation else value

        value = cls._enforce_dict_if_root(value)
        if isinstance(value, dict):
            return cls(**value)
        elif cls.__config__.orm_mode:
            return cls.from_orm(value)
        else:
            try:
                value_as_dict = dict(value)
            except (TypeError, ValueError) as e:
                raise DictError() from e
            return cls(**value_as_dict)