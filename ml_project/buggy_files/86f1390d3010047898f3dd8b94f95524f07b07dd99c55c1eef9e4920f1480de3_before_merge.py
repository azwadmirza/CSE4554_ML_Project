    async def create_source_event_stream(
        self,
        execution_ctx: ExecutionContext,
        request_ctx: Optional[Dict[str, Any]],
        parent_result: Optional[Any] = None,
    ):
        if not self.subscribe:
            raise GraphQLError(
                "Can't execute a subscription query on a field which doesn't "
                "provide a source event stream with < @Subscription >."
            )

        # TODO: refactor this to have re-usable code with `_ResolverExecutor`
        arguments = (
            self.field_executor.schema_field.get_arguments_default_values()
        )
        arguments.update(
            {
                argument.name: argument.value
                for argument in self.arguments.values()
            }
        )

        return self.subscribe(
            parent_result,
            arguments,
            request_ctx,
            Info(
                query_field=self,
                schema_field=self.field_executor.schema_field,
                schema=self.schema,
                path=self.path,
                location=self.location,
                execution_ctx=execution_ctx,
            ),
        )