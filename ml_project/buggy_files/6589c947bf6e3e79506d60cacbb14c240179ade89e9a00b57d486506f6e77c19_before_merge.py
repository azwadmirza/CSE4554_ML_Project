def list_secrets(path):
    """
    List secret keys at the path in vault. The vault policy used must allow this.
    The path should end with a trailing slash.

    CLI Example:

    .. code-block:: bash

            salt '*' vault.list_secrets "secret/my/"
    """
    log.debug("Listing vault secret keys for %s in %s", __grains__["id"], path)
    try:
        url = "v1/{0}".format(path)
        response = __utils__["vault.make_request"]("LIST", url)
        if response.status_code != 200:
            response.raise_for_status()
        return response.json()["data"]
    except Exception as err:  # pylint: disable=broad-except
        log.error("Failed to list secrets! %s: %s", type(err).__name__, err)
        return None