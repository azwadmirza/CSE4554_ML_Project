    def resolve(self, schema: s_schema.Schema) -> Array:
        return schema.get_by_id(self.get_id(schema), type=Array)