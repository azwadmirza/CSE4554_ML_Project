    def validate(cls: Type['Model'], value: Any) -> 'Model':
        if isinstance(value, dict):
            return cls(**value)
        elif isinstance(value, cls):
            return value.copy()
        elif cls.__config__.orm_mode:
            return cls.from_orm(value)
        elif cls.__custom_root_type__:
            return cls.parse_obj(value)
        else:
            try:
                value_as_dict = dict(value)
            except (TypeError, ValueError) as e:
                raise DictError() from e
            return cls(**value_as_dict)