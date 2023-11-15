    def list_length_validator(cls, v: 'Optional[List[T]]', field: 'ModelField') -> 'Optional[List[T]]':
        if v is None and not field.required:
            return None

        v = list_validator(v)
        v_len = len(v)

        if cls.min_items is not None and v_len < cls.min_items:
            raise errors.ListMinLengthError(limit_value=cls.min_items)

        if cls.max_items is not None and v_len > cls.max_items:
            raise errors.ListMaxLengthError(limit_value=cls.max_items)

        return v