def set_(key, value, profile=None):
    """
    Set a key/value pair in the vault service
    """
    if "?" in key:
        path, key = key.split("?")
    else:
        path, key = key.rsplit("/", 1)
    data = {key: value}

    version2 = __utils__["vault.is_v2"](path)
    if version2["v2"]:
        path = version2["data"]
        data = {"data": data}

    try:
        url = "v1/{0}".format(path)
        response = __utils__["vault.make_request"]("POST", url, json=data)

        if response.status_code != 204:
            response.raise_for_status()
        return True
    except Exception as e:  # pylint: disable=broad-except
        log.error("Failed to write secret! %s: %s", type(e).__name__, e)
        raise salt.exceptions.CommandExecutionError(e)