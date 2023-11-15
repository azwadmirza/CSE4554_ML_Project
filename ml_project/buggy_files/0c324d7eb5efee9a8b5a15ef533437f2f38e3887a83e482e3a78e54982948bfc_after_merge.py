    def get_subtypes(self, schema: s_schema.Schema) -> typing.Tuple[Type, ...]:
        return self.get_element_types(schema).values(schema)