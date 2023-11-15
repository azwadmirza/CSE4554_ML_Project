def write_secret(path, **kwargs):
    """
    Set secret at the path in vault. The vault policy used must allow this.

    CLI Example:

    .. code-block:: bash

            salt '*' vault.write_secret "secret/my/secret" user="foo" password="bar"
    """
    log.debug("Writing vault secrets for %s at %s", __grains__["id"], path)
    data = dict([(x, y) for x, y in kwargs.items() if not x.startswith("__")])
    version2 = __utils__["vault.is_v2"](path)
    if version2["v2"]:
        path = version2["data"]
        data = {"data": data}
    try:
        url = "v1/{0}".format(path)
        response = __utils__["vault.make_request"]("POST", url, json=data)
        if response.status_code == 200:
            return response.json()["data"]
        elif response.status_code != 204:
            response.raise_for_status()
        return True
    except Exception as err:  # pylint: disable=broad-except
        log.error("Failed to write secret! %s: %s", type(err).__name__, err)
        return False