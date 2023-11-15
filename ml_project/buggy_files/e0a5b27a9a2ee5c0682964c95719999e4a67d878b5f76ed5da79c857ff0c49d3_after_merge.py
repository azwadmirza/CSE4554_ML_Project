def tables(
    limit: int = 100,
    catalog_id: Optional[str] = None,
    database: Optional[str] = None,
    search_text: Optional[str] = None,
    name_contains: Optional[str] = None,
    name_prefix: Optional[str] = None,
    name_suffix: Optional[str] = None,
    boto3_session: Optional[boto3.Session] = None,
) -> pd.DataFrame:
    """Get a DataFrame with tables filtered by a search term, prefix, suffix.

    Parameters
    ----------
    limit : int, optional
        Max number of tables to be returned.
    catalog_id : str, optional
        The ID of the Data Catalog from which to retrieve Databases.
        If none is provided, the AWS account ID is used by default.
    database : str, optional
        Database name.
    search_text : str, optional
        Select only tables with the given string in table's properties.
    name_contains : str, optional
        Select by a specific string on table name
    name_prefix : str, optional
        Select by a specific prefix on table name
    name_suffix : str, optional
        Select by a specific suffix on table name
    boto3_session : boto3.Session(), optional
        Boto3 Session. The default boto3 session will be used if boto3_session receive None.

    Returns
    -------
    Iterator[Dict[str, Any]]
        Pandas Dataframe filled by formatted infos.

    Examples
    --------
    >>> import awswrangler as wr
    >>> df_tables = wr.catalog.tables()

    """
    if search_text is None:
        table_iter = get_tables(
            catalog_id=catalog_id,
            database=database,
            name_contains=name_contains,
            name_prefix=name_prefix,
            name_suffix=name_suffix,
            boto3_session=boto3_session,
        )
        tbls: List[Dict[str, Any]] = list(itertools.islice(table_iter, limit))
    else:
        tbls = list(search_tables(text=search_text, catalog_id=catalog_id, boto3_session=boto3_session))
        if database is not None:
            tbls = [x for x in tbls if x["DatabaseName"] == database]
        if name_contains is not None:
            tbls = [x for x in tbls if name_contains in x["Name"]]
        if name_prefix is not None:
            tbls = [x for x in tbls if x["Name"].startswith(name_prefix)]
        if name_suffix is not None:
            tbls = [x for x in tbls if x["Name"].endswith(name_suffix)]
        tbls = tbls[:limit]

    df_dict: Dict[str, List] = {"Database": [], "Table": [], "Description": [], "Columns": [], "Partitions": []}
    for tbl in tbls:
        df_dict["Database"].append(tbl["DatabaseName"])
        df_dict["Table"].append(tbl["Name"])
        df_dict["Description"].append(tbl.get("Description", ""))
        if "Columns" in tbl["StorageDescriptor"]:
            df_dict["Columns"].append(", ".join([x["Name"] for x in tbl["StorageDescriptor"]["Columns"]]))
        else:
            df_dict["Columns"].append("")  # pragma: no cover
        if "PartitionKeys" in tbl:
            df_dict["Partitions"].append(", ".join([x["Name"] for x in tbl["PartitionKeys"]]))
        else:
            df_dict["Partitions"].append("")  # pragma: no cover
    return pd.DataFrame(data=df_dict)