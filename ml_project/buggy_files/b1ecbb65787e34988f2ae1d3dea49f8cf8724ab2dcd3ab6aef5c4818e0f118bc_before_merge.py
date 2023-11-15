def create_context_with_type(
    store,
    context_name: str,
    type_name: str,
    properties: dict = None,
    type_properties: dict = None,
) -> metadata_store_pb2.Context:
    # ! Context_name must be unique
    context_type = get_or_create_context_type(
        store=store,
        type_name=type_name,
        properties=type_properties,
    )
    context = metadata_store_pb2.Context(
        name=context_name,
        type_id=context_type.id,
        properties=properties,
    )
    context.id = store.put_contexts([context])[0]
    return context