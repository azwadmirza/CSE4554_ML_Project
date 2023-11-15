    def get_name(
        self,
        schema: s_schema.Schema,
    ) -> s_name.Name:
        _, name = get_intersection_type_id(
            schema,
            self.components,
            module=self.module,
        )
        return name