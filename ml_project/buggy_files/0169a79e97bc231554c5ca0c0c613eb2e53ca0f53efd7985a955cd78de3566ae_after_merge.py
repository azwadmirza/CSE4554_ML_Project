def get_or_create_context_with_type(
    store,
    context_name: str,
    type_name: str,
    properties: dict = None,
    type_properties: dict = None,
    custom_properties: dict = None,
) -> metadata_store_pb2.Context:
    try:
        context = get_context_by_name(store, context_name)
    except:
        context = create_context_with_type(
            store=store,
            context_name=context_name,
            type_name=type_name,
            properties=properties,
            type_properties=type_properties,
            custom_properties=custom_properties,
        )
        return context

    # Verifying that the context has the expected type name
    context_types = store.get_context_types_by_id([context.type_id])
    assert len(context_types) == 1
    if context_types[0].name != type_name:
        raise RuntimeError('Context "{}" was found, but it has type "{}" instead of "{}"'.format(context_name, context_types[0].name, type_name))
    return context