    def resolve(self, schema: s_schema.Schema) -> Tuple:
        return schema.get_by_id(self.get_id(schema), type=Tuple)