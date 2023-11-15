    def _extend_query_type(self):
        fields = {"_service": self._service_field}

        entity_type = _get_entity_type(self.type_map)

        if entity_type:
            self._schema.type_map[entity_type.name] = entity_type

            fields["_entities"] = self._get_entities_field(entity_type)

        fields.update(self._schema.query_type.fields)

        self._schema.query_type = GraphQLObjectType(
            name=self._schema.query_type.name,
            description=self._schema.query_type.description,
            fields=fields,
        )

        self._schema.type_map["_Service"] = self._service_type
        self._schema.type_map[self._schema.query_type.name] = self._schema.query_type