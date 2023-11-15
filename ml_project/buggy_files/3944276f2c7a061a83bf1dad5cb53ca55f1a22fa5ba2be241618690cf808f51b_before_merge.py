    def _prepare_id(
        cls, id: Optional[uuid.UUID], data: Dict[str, Any]
    ) -> uuid.UUID:
        if id is not None:
            return id

        name = data.get('name')
        assert isinstance(name, (str, sn.Name))

        try:
            return get_known_type_id(name)
        except errors.SchemaError:
            return uuidgen.uuid1mc()