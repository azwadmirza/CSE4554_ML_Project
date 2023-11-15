    def get_id(self, schema: s_schema.Schema) -> uuid.UUID:
        name = self.get_name(schema)
        stable_type_id = type_id_from_name(name)
        if stable_type_id is not None:
            return stable_type_id

        named = self.is_named()

        quals: typing.List[str] = [str(name)]
        if self.expr is not None:
            quals.append(self.expr)

        return generate_tuple_type_id(schema, self.subtypes, named, *quals)