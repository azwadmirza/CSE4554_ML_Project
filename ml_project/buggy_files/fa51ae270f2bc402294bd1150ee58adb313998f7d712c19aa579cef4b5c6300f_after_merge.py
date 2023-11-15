    def bake(self, schema: "GraphQLSchema") -> None:
        self._schema = schema
        self._directives_implementations = get_directive_implem_list(
            self._directives, self._schema
        )
        if isinstance(self.gql_type, GraphQLType):
            self._type = self.gql_type
        else:
            self._type["name"] = self.gql_type
            self._type["kind"] = self._schema.find_type(self.gql_type).kind