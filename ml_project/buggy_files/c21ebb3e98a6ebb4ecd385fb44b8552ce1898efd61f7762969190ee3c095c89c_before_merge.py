    def material_type(
        self: Tuple_T,
        schema: s_schema.Schema,
    ) -> typing.Tuple[s_schema.Schema, Tuple_T]:
        # We need to resolve material types of all the subtypes recursively.
        new_material_type = False
        subtypes = {}

        for st_name, st in self.iter_subtypes(schema):
            schema, stm = st.material_type(schema)
            if stm != st:
                new_material_type = True
            subtypes[st_name] = stm

        if new_material_type or str(self.get_name(schema)) != str(self.id):
            return self.__class__.from_subtypes(
                schema, subtypes, typemods=self.get_typemods(schema))
        else:
            return schema, self