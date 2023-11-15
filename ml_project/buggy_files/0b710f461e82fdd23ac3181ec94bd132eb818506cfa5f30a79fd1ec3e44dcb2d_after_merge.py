    def get_name(self, schema: s_schema.Schema) -> s_name.Name:
        if str(self.name) == '__unresolved__':
            self.name = self.schemaclass.generate_name(
                self.subtype.get_name(schema),
            )

        return self.name