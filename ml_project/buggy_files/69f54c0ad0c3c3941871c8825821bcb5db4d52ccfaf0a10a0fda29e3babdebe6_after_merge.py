def create_new_execution_in_existing_run_context(
    store,
    execution_type_name: str,
    context_id: int,
    pod_name: str,
    # TODO: Remove when UX stops relying on thsese properties
    pipeline_name: str = None,
    run_id: str = None,
    instance_id: str = None,
    custom_properties = None,
) -> metadata_store_pb2.Execution:
    pipeline_name = pipeline_name or 'Context_' + str(context_id) + '_pipeline'
    run_id = run_id or 'Context_' + str(context_id) + '_run'
    instance_id = instance_id or execution_type_name
    return create_new_execution_in_existing_context(
        store=store,
        execution_type_name=execution_type_name,
        context_id=context_id,
        execution_type_properties={
            EXECUTION_PIPELINE_NAME_PROPERTY_NAME: metadata_store_pb2.STRING,
            EXECUTION_RUN_ID_PROPERTY_NAME: metadata_store_pb2.STRING,
            EXECUTION_COMPONENT_ID_PROPERTY_NAME: metadata_store_pb2.STRING,
        },
        # TODO: Remove when UX stops relying on thsese properties
        properties={
            EXECUTION_PIPELINE_NAME_PROPERTY_NAME: metadata_store_pb2.Value(string_value=pipeline_name), # Mistakenly used for grouping in the UX
            EXECUTION_RUN_ID_PROPERTY_NAME: metadata_store_pb2.Value(string_value=run_id),
            EXECUTION_COMPONENT_ID_PROPERTY_NAME: metadata_store_pb2.Value(string_value=instance_id), # should set to task ID, not component ID
        },
        custom_properties={
            KFP_POD_NAME_EXECUTION_PROPERTY_NAME: metadata_store_pb2.Value(string_value=pod_name),
        },
    )