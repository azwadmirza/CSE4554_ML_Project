def get_bigquery_client(credentials: dict = None, project: str = None):
    """
    Utility function for instantiating a Google BigQuery Client from a given set of credentials.

    Args:
        - credentials (dict, optional): a dictionary of Google credentials used to initialize the Client; if
            not provided, will attempt to load the Client using ambient environment settings
        - project (str, optional): the Google project to point the Client to; if not provided, Client defaults
            will be used

    Returns:
        - Client: an initialized and authenticated Google Client
    """
    from google.cloud import bigquery

    return get_google_client(bigquery, credentials=credentials, project=project)