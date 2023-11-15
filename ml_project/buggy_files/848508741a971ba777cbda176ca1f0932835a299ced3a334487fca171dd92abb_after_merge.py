def get_connection(
    name: str, catalog_id: Optional[str] = None, boto3_session: Optional[boto3.Session] = None
) -> Dict[str, Any]:
    """Get Glue connection details.

    Parameters
    ----------
    name : str
        Connection name.
    catalog_id : str, optional
        The ID of the Data Catalog from which to retrieve Databases.
        If none is provided, the AWS account ID is used by default.
    boto3_session : boto3.Session(), optional
        Boto3 Session. The default boto3 session will be used if boto3_session receive None.

    Returns
    -------
    Dict[str, Any]
        API Response for:
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue.html#Glue.Client.get_connection

    Examples
    --------
    >>> import awswrangler as wr
    >>> res = wr.catalog.get_connection(name='my_connection')

    """
    client_glue: boto3.client = _utils.client(service_name="glue", session=boto3_session)

    res = _utils.try_it(
        f=client_glue.get_connection,
        ex=botocore.exceptions.ClientError,
        ex_code="ThrottlingException",
        max_num_tries=3,
        **_catalog_id(catalog_id=catalog_id, Name=name, HidePassword=False),
    )["Connection"]

    if "ENCRYPTED_PASSWORD" in res["ConnectionProperties"]:
        client_kms = _utils.client(service_name="kms", session=boto3_session)
        pwd = client_kms.decrypt(CiphertextBlob=base64.b64decode(res["ConnectionProperties"]["ENCRYPTED_PASSWORD"]))[
            "Plaintext"
        ]
        res["ConnectionProperties"]["PASSWORD"] = pwd
    return cast(Dict[str, Any], res)