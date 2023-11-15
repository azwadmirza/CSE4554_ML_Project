async def execute(
    schema: GraphQLSchema,
    query: str,
    root_value: typing.Any = None,
    context_value: typing.Any = None,
    variable_values: typing.Dict[str, typing.Any] = None,
    middleware: typing.List[Middleware] = None,
    operation_name: str = None,
):  # pragma: no cover
    schema_validation_errors = validate_schema(schema)
    if schema_validation_errors:
        return ExecutionResult(data=None, errors=schema_validation_errors)

    try:
        document = parse(query)
    except GraphQLError as error:
        return ExecutionResult(data=None, errors=[error])
    except Exception as error:
        error = GraphQLError(str(error), original_error=error)
        return ExecutionResult(data=None, errors=[error])

    validation_errors = validate(schema, document)

    if validation_errors:
        return ExecutionResult(data=None, errors=validation_errors)

    result = graphql_execute(
        schema,
        parse(query),
        root_value=root_value,
        middleware=middleware or [],
        variable_values=variable_values,
        operation_name=operation_name,
        context_value=context_value,
    )
    if isawaitable(result):
        result = await typing.cast(typing.Awaitable[ExecutionResult], result)
    return result