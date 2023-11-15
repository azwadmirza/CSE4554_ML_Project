def get_flat_models_from_routes(
    routes: Sequence[Type[BaseRoute]]
) -> Set[Type[BaseModel]]:
    body_fields_from_routes: List[Field] = []
    responses_from_routes: List[Field] = []
    for route in routes:
        if getattr(route, "include_in_schema", None) and isinstance(
            route, routing.APIRoute
        ):
            if route.body_field:
                assert isinstance(
                    route.body_field, Field
                ), "A request body must be a Pydantic Field"
                body_fields_from_routes.append(route.body_field)
            if route.response_field:
                responses_from_routes.append(route.response_field)
            if route.response_fields:
                responses_from_routes.extend(route.response_fields.values())
    flat_models = get_flat_models_from_fields(
        body_fields_from_routes + responses_from_routes
    )
    return flat_models