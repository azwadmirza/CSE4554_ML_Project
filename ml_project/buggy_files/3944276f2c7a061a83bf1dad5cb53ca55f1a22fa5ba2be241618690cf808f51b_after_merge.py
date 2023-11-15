    def _prepare_id(
        cls,
        schema: s_schema.Schema,
        data: Dict[str, Any],
    ) -> uuid.UUID:
        name = data.get('name')
        assert isinstance(name, (str, sn.Name))

        try:
            return get_known_type_id(name)
        except errors.SchemaError:
            return cls.generate_id(schema, data)