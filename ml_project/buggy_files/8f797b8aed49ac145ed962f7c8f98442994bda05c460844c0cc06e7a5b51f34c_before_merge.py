    def get_name(
        self,
        schema: s_schema.Schema,
    ) -> s_name.Name:
        _, name = get_union_type_id(
            schema,
            self.components,
            opaque=self.opaque,
            module=self.module,
        )
        return name