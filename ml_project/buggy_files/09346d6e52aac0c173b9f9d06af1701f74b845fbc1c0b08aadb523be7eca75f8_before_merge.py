def get(key, profile=None):
    """
    Get a value from the vault service
    """
    if "?" in key:
        path, key = key.split("?")
    else:
        path, key = key.rsplit("/", 1)

    try:
        url = "v1/{0}".format(path)
        response = __utils__["vault.make_request"]("GET", url, profile)
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            response.raise_for_status()
        data = response.json()["data"]

        if key in data:
            return data[key]
        return None
    except Exception as e:  # pylint: disable=broad-except
        log.error("Failed to read secret! %s: %s", type(e).__name__, e)
        raise salt.exceptions.CommandExecutionError(e)