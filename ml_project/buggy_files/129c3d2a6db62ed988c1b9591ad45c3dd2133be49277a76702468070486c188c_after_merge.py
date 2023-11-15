    def resolve(self, schema: s_schema.Schema) -> Array:
        if isinstance(self.name, s_name.QualName):
            return schema.get(self.name, type=Array)
        else:
            return schema.get_by_id(self.get_id(schema), type=Array)