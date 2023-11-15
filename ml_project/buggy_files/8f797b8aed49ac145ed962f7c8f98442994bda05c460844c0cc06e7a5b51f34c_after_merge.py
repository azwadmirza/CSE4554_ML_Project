    def get_name(
        self,
        schema: s_schema.Schema,
    ) -> s_name.Name:
        return get_union_type_name(
            (c.get_name(schema) for c in self.components),
            opaque=self.opaque,
            module=self.module,
        )