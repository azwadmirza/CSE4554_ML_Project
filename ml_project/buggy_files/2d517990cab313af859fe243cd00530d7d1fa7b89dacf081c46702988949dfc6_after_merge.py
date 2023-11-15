    async def execute(self, query, variables=None, context=None, operation_name=None):
        if self.debug:
            pretty_print_graphql_operation(operation_name, query, variables)

        return await self.schema.execute(
            query,
            root_value=self.root_value,
            variable_values=variables,
            operation_name=operation_name,
            context_value=context,
        )