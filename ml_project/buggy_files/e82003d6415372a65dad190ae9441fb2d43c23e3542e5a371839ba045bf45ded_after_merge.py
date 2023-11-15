def get_table_description(
    database: str, table: str, catalog_id: Optional[str] = None, boto3_session: Optional[boto3.Session] = None
) -> Optional[str]:
    """Get table description.

    Parameters
    ----------
    database : str
        Database name.
    table : str
        Table name.
    catalog_id : str, optional
        The ID of the Data Catalog from which to retrieve Databases.
        If none is provided, the AWS account ID is used by default.
    boto3_session : boto3.Session(), optional
        Boto3 Session. The default boto3 session will be used if boto3_session receive None.

    Returns
    -------
    Optional[str]
        Description if exists.

    Examples
    --------
    >>> import awswrangler as wr
    >>> desc = wr.catalog.get_table_description(database="...", table="...")

    """
    client_glue: boto3.client = _utils.client(service_name="glue", session=boto3_session)
    args: Dict[str, str] = {}
    if catalog_id is not None:
        args["CatalogId"] = catalog_id  # pragma: no cover
    args["DatabaseName"] = database
    args["Name"] = table
    response: Dict[str, Any] = client_glue.get_table(**args)
    desc: Optional[str] = response["Table"].get("Description", None)
    return desc