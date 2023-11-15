    def get_name(self, schema: s_schema.Schema) -> s_name.Name:
        if str(self.name) == '__unresolved__':
            typemods = self.typemods
            subtypes = self.subtypes
            named = typemods is not None and typemods.get('named', False)
            tid = generate_tuple_type_id(schema, subtypes, named)
            st_names = ', '.join(
                st.get_displayname(schema) for st in subtypes.values()
            )
            name = type_name_from_id_and_displayname(tid, f'tuple<{st_names}>')
            self.name = name
        return self.name