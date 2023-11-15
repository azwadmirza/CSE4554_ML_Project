    def get_name(
        self,
        schema: s_schema.Schema,
    ) -> s_name.Name:
        return get_intersection_type_name(
            (c.get_name(schema) for c in self.components),
            module=self.module,
        )