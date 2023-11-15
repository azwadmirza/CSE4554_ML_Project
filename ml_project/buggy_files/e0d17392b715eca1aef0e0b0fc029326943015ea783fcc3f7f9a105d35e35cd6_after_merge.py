    def init_delta_command(
        self: Object_T,
        schema: s_schema.Schema,
        cmdtype: Type[sd.ObjectCommand_T],
        *,
        classname: Optional[sn.Name] = None,
        **kwargs: Any,
    ) -> sd.ObjectCommand_T:
        from . import delta as sd

        cls = type(self)
        cmd = sd.get_object_delta_command(
            objtype=cls,
            cmdtype=cmdtype,
            schema=schema,
            name=classname or self.get_name(schema),
            ddl_identity=self.get_ddl_identity(schema),
            **kwargs,
        )
        self.record_cmd_object_aux_data(schema, cmd)
        return cmd