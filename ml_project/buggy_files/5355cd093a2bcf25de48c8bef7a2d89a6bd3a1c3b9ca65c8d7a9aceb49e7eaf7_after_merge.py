    def get_id(self, schema: s_schema.Schema) -> uuid.UUID:
        return generate_tuple_type_id(schema, self.subtypes, self.is_named())