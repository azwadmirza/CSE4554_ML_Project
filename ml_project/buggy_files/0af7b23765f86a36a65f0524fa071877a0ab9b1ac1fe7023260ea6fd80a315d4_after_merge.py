    def get_name(self, schema: s_schema.Schema) -> s_name.Name:
        if str(self.name) == '__unresolved__':
            typemods = self.typemods
            subtypes = self.subtypes
            named = typemods is not None and typemods.get('named', False)
            self.name = self.schemaclass.generate_name(
                {n: st.get_name(schema) for n, st in subtypes.items()},
                named,
            )
        return self.name