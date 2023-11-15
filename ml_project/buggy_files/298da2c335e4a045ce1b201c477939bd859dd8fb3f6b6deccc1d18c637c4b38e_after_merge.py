def read_secret(path, key=None, metadata=False):
    """
    Return the value of key at path in vault, or entire secret

    :param metadata: Optional - If using KV v2 backend, display full results, including metadata

        .. versionadded:: Sodium

    Jinja Example:

    .. code-block:: jinja

        my-secret: {{ salt['vault'].read_secret('secret/my/secret', 'some-key') }}

        {{ salt['vault'].read_secret('/secret/my/secret', 'some-key', metadata=True)['data'] }}

    .. code-block:: jinja

        {% set supersecret = salt['vault'].read_secret('secret/my/secret') %}
        secrets:
            first: {{ supersecret.first }}
            second: {{ supersecret.second }}
    """
    version2 = __utils__["vault.is_v2"](path)
    if version2["v2"]:
        path = version2["data"]
    log.debug("Reading Vault secret for %s at %s", __grains__["id"], path)
    try:
        url = "v1/{0}".format(path)
        response = __utils__["vault.make_request"]("GET", url)
        if response.status_code != 200:
            response.raise_for_status()
        data = response.json()["data"]

        # Return data of subkey if requested
        if key is not None:
            if version2["v2"]:
                return data["data"][key]
            else:
                return data[key]
        # Just return data from KV V2 if metadata isn't needed
        if version2["v2"]:
            if not metadata:
                return data["data"]

        return data
    except Exception as err:  # pylint: disable=broad-except
        log.error("Failed to read secret! %s: %s", type(err).__name__, err)
        return None