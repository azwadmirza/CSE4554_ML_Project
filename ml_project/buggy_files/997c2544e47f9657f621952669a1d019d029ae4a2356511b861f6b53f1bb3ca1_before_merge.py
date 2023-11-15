def create_artifact_with_type(
    store,
    uri: str,
    type_name: str,
    properties: dict = None,
    type_properties: dict = None,
) -> metadata_store_pb2.Artifact:
    artifact_type = get_or_create_artifact_type(
        store=store,
        type_name=type_name,
        properties=type_properties,
    )
    artifact = metadata_store_pb2.Artifact(
        uri=uri,
        type_id=artifact_type.id,
        properties=properties,
    )
    artifact.id = store.put_artifacts([artifact])[0]
    return artifact