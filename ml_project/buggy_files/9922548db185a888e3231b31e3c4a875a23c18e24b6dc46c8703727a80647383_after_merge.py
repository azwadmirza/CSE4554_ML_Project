def _get_table_input(
    database: str, table: str, boto3_session: Optional[boto3.Session], catalog_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    client_glue: boto3.client = _utils.client(service_name="glue", session=boto3_session)
    args: Dict[str, str] = {}
    if catalog_id is not None:
        args["CatalogId"] = catalog_id  # pragma: no cover
    args["DatabaseName"] = database
    args["Name"] = table
    try:
        response: Dict[str, Any] = client_glue.get_table(**args)
    except client_glue.exceptions.EntityNotFoundException:
        return None

    table_input: Dict[str, Any] = {}
    for k, v in response["Table"].items():
        if k in [
            "Name",
            "Description",
            "Owner",
            "LastAccessTime",
            "LastAnalyzedTime",
            "Retention",
            "StorageDescriptor",
            "PartitionKeys",
            "ViewOriginalText",
            "ViewExpandedText",
            "TableType",
            "Parameters",
            "TargetTable",
        ]:
            table_input[k] = v

    return table_input