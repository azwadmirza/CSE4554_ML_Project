def _get_table_input(
    database: str, table: str, boto3_session: Optional[boto3.Session], catalog_id: Optional[str] = None
) -> Optional[Dict[str, str]]:
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
    if "DatabaseName" in response["Table"]:
        del response["Table"]["DatabaseName"]
    if "CreateTime" in response["Table"]:
        del response["Table"]["CreateTime"]
    if "UpdateTime" in response["Table"]:
        del response["Table"]["UpdateTime"]
    if "CreatedBy" in response["Table"]:
        del response["Table"]["CreatedBy"]
    if "IsRegisteredWithLakeFormation" in response["Table"]:
        del response["Table"]["IsRegisteredWithLakeFormation"]
    return response["Table"]