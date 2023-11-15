    def _preheat(schema_name: str) -> "GraphQLSchema":
        """
        Loads the SDL and converts it to a GraphQLSchema instance before baking
        each registered objects of this schema.
        :param schema_name: name of the schema to treat
        :type schema_name: str
        :return: a pre-baked GraphQLSchema instance
        :rtype: GraphQLSchema
        """
        schema_info = SchemaRegistry.find_schema_info(schema_name)
        sdl = schema_info["sdl"]

        schema = schema_from_sdl(sdl, schema_name=schema_name)

        for object_ids in _SCHEMA_OBJECT_IDS:
            for obj in schema_info.get(object_ids, {}).values():
                obj.bake(schema)

        schema_info["inst"] = schema

        return schema