def create_execution_with_type(
    store,
    type_name: str,
    properties: dict = None,
    type_properties: dict = None,
    custom_properties: dict = None,
) -> metadata_store_pb2.Execution:
    execution_type = get_or_create_execution_type(
        store=store,
        type_name=type_name,
        properties=type_properties,
    )
    execution = metadata_store_pb2.Execution(
        type_id=execution_type.id,
        properties=properties,
        custom_properties=custom_properties,
    )
    execution.id = store.put_executions([execution])[0]
    return execution