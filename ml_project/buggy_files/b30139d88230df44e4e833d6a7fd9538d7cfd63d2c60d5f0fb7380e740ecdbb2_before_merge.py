    def _extend_query_type(self):
        @type(name="_Service")
        class Service:
            sdl: str

        Any = GraphQLScalarType("_Any")

        fields = {
            "_service": GraphQLField(
                GraphQLNonNull(Service.graphql_type),
                resolve=lambda _, info: Service(sdl=print_schema(info.schema)),
            )
        }

        entities_type = self._get_entity_type()

        if entities_type:
            self.type_map[entities_type.name] = entities_type

            fields["_entities"] = GraphQLField(
                GraphQLNonNull(GraphQLList(entities_type)),
                args={
                    "representations": GraphQLNonNull(GraphQLList(GraphQLNonNull(Any)))
                },
                resolve=entities_resolver,
            )

        fields.update(self.query_type.fields)

        self.query_type = GraphQLObjectType(
            name=self.query_type.name,
            description=self.query_type.description,
            fields=fields,
        )

        self.type_map["_Any"] = Any
        self.type_map["_Service"] = Service.graphql_type
        self.type_map[self.query_type.name] = self.query_type