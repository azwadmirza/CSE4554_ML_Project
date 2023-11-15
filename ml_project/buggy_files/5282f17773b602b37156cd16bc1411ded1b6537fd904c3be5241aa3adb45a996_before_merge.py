    def _get_entity_type(self):
        # https://www.apollographql.com/docs/apollo-server/federation/federation-spec/#resolve-requests-for-entities

        # To implement the _Entity union, each type annotated with @key
        # should be added to the _Entity union.

        federation_key_types = [
            graphql_type
            for graphql_type in self.type_map.values()
            if has_federation_keys(graphql_type)
        ]

        # If no types are annotated with the key directive, then the _Entity
        # union and Query._entities field should be removed from the schema.
        if not federation_key_types:
            return None

        entity_type = GraphQLUnionType("_Entity", federation_key_types)

        def _resolve_type(self, value, _type):
            return self.graphql_type

        entity_type.resolve_type = _resolve_type

        return entity_type