def create_new_execution_in_existing_context(
    store,
    execution_type_name: str,
    context_id: int,
    properties: dict = None,
    execution_type_properties: dict = None,
    custom_properties: dict = None,
) -> metadata_store_pb2.Execution:
    execution = create_execution_with_type(
        store=store,
        properties=properties,
        custom_properties=custom_properties,
        type_name=execution_type_name,
        type_properties=execution_type_properties,
    )
    association = metadata_store_pb2.Association(
        execution_id=execution.id,
        context_id=context_id,
    )

    store.put_attributions_and_associations([], [association])
    return execution