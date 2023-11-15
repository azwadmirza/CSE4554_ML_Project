    def get_subtypes(self, schema: s_schema.Schema) -> typing.Tuple[Type, ...]:
        return self.get_element_types(schema).values(schema)

        if self.element_types:
            return self.element_types.objects(schema)
        else:
            return []