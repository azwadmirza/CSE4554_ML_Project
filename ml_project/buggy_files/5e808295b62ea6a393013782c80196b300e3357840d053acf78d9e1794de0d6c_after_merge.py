    def resolve(self, schema: s_schema.Schema) -> Type:
        return schema.get(
            self.get_name(schema),
            type=self.schemaclass,
            sourcectx=self.sourcectx,
        )