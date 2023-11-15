    def get_id(self, schema: s_schema.Schema) -> uuid.UUID:
        return generate_array_type_id(schema, self.subtype, self.typemods[0])