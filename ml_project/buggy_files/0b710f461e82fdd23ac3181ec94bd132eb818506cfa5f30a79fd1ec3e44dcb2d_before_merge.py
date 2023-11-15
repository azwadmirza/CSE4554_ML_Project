    def get_name(self, schema: s_schema.Schema) -> s_name.Name:
        if str(self.name) == '__unresolved__':
            typemods = self.typemods
            dimensions = typemods[0]
            tid = generate_array_type_id(schema, self.subtype, dimensions)
            self.name = type_name_from_id_and_displayname(
                tid, f'array<{self.subtype.get_displayname(schema)}>')
        return self.name