    def _validate_non_empty_object(self) -> List[str]:
        """
        Validates that object types implement at least one fields.
        :return: a list of errors
        :rtype: List[str]
        """
        errors = []
        for type_name, gql_type in self.type_definitions.items():
            if isinstance(gql_type, GraphQLObjectType) and not [
                field_name
                for field_name in gql_type.implemented_fields
                if not field_name.startswith("__")
            ]:
                errors.append(f"Type < {type_name} > has no fields.")
        return errors