    def resolve(self, schema: s_schema.Schema) -> Type:
        return schema.get(
            self.name,
            type=self.schemaclass,
            sourcectx=self.sourcectx,
        )