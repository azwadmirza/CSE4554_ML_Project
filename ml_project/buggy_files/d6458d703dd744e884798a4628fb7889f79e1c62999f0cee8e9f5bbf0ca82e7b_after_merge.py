def databases(
    limit: int = 100, catalog_id: Optional[str] = None, boto3_session: Optional[boto3.Session] = None
) -> pd.DataFrame:
    """Get a Pandas DataFrame with all listed databases.

    Parameters
    ----------
    limit : int, optional
        Max number of tables to be returned.
    catalog_id : str, optional
        The ID of the Data Catalog from which to retrieve Databases.
        If none is provided, the AWS account ID is used by default.
    boto3_session : boto3.Session(), optional
        Boto3 Session. The default boto3 session will be used if boto3_session receive None.

    Returns
    -------
    pandas.DataFrame
        Pandas DataFrame filled by formatted infos.

    Examples
    --------
    >>> import awswrangler as wr
    >>> df_dbs = wr.catalog.databases()

    """
    database_iter: Iterator[Dict[str, Any]] = get_databases(catalog_id=catalog_id, boto3_session=boto3_session)
    dbs = itertools.islice(database_iter, limit)
    df_dict: Dict[str, List] = {"Database": [], "Description": []}
    for db in dbs:
        df_dict["Database"].append(db["Name"])
        df_dict["Description"].append(db.get("Description", ""))
    return pd.DataFrame(data=df_dict)