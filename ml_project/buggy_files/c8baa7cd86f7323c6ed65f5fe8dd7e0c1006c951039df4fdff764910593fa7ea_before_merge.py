def _get_credentials(credentials_name: str, credentials: Dict) -> Dict:
    """Return a set of credentials from the provided credentials dict.

    Args:
        credentials_name: Credentials name.
        credentials: A dictionary with all credentials.

    Returns:
        The set of requested credentials.

    Raises:
        KeyError: When a data set with the given name has not yet been
            registered.

    """
    try:
        return credentials[credentials_name]
    except KeyError:
        raise KeyError(
            "Unable to find credentials '{}': check your data "
            "catalog and credentials configuration. See "
            "https://kedro.readthedocs.io/en/latest/kedro.io.DataCatalog.html "
            "for an example.".format(credentials_name)
        )