def write_raw(path, raw):
    """
    Set raw data at the path in vault. The vault policy used must allow this.

    CLI Example:

    .. code-block:: bash

            salt '*' vault.write_raw "secret/my/secret" '{"user":"foo","password": "bar"}'
    """
    log.debug("Writing vault secrets for %s at %s", __grains__["id"], path)
    try:
        url = "v1/{0}".format(path)
        response = __utils__["vault.make_request"]("POST", url, json=raw)
        if response.status_code == 200:
            return response.json()["data"]
        elif response.status_code != 204:
            response.raise_for_status()
        return True
    except Exception as err:  # pylint: disable=broad-except
        log.error("Failed to write secret! %s: %s", type(err).__name__, err)
        return False