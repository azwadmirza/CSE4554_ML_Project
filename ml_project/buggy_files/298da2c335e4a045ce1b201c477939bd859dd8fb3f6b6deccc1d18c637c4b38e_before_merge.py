def read_secret(path, key=None):
    """
    Return the value of key at path in vault, or entire secret

    Jinja Example:

    .. code-block:: jinja

        my-secret: {{ salt['vault'].read_secret('secret/my/secret', 'some-key') }}

    .. code-block:: jinja

        {% set supersecret = salt['vault'].read_secret('secret/my/secret') %}
        secrets:
            first: {{ supersecret.first }}
            second: {{ supersecret.second }}
    """
    log.debug("Reading Vault secret for %s at %s", __grains__["id"], path)
    try:
        url = "v1/{0}".format(path)
        response = __utils__["vault.make_request"]("GET", url)
        if response.status_code != 200:
            response.raise_for_status()
        data = response.json()["data"]

        if key is not None:
            return data[key]
        return data
    except Exception as err:  # pylint: disable=broad-except
        log.error("Failed to read secret! %s: %s", type(err).__name__, err)
        return None