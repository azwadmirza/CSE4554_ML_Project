    def create_in_schema(
        cls: Type[Object_T],
        schema: s_schema.Schema,
        *,
        id: Optional[uuid.UUID] = None,
        **data: Any,
    ) -> Tuple[s_schema.Schema, Object_T]:

        if not cls.is_schema_object:
            raise TypeError(f'{cls.__name__} type cannot be created in schema')

        if not data.get('name'):
            raise RuntimeError(f'cannot create {cls} without a name')

        all_fields = cls.get_schema_fields()
        obj_data = [None] * len(all_fields)
        for field_name, value in data.items():
            field = cls.get_schema_field(field_name)
            value = field.coerce_value(schema, value)
            obj_data[field.index] = value

        if id is None:
            id = cls._prepare_id(schema, data)
        scls = cls._create_from_id(id)
        schema = schema.add(id, cls, tuple(obj_data))

        return schema, scls