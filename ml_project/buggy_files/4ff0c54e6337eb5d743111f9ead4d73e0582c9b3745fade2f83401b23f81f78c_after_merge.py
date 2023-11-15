    def prepare(self, stream, schema, extra):

        # Prepare package
        if 'datapackage' not in extra or 'resource-name' not in extra:
            return False
        descriptor = extra['datapackage']
        if descriptor.strip().startswith('{'):
            descriptor = json.loads(descriptor)
        self.__package = datapackage.Package(descriptor)

        # Prepare schema
        if not schema:
            return False
        if not schema.foreign_keys:
            return False
        self.__schema = schema

        # Prepare foreign keys values
        try:
            self.__relations = _get_relations(
                self.__package, self.__schema,
                current_resource_name=extra['resource-name'])
            self.__foreign_keys_values = _get_foreign_keys_values(
                self.__schema, self.__relations)
            self.__relations_exception = None
        except _ReferenceTableError as exception:
            self.__relations_exception = exception

        return True