def delete_secret(path):
    """
    Delete secret at the path in vault. The vault policy used must allow this.

    CLI Example:

    .. code-block:: bash

        salt '*' vault.delete_secret "secret/my/secret"
    """
    log.debug("Deleting vault secrets for %s in %s", __grains__["id"], path)
    try:
        url = "v1/{0}".format(path)
        response = __utils__["vault.make_request"]("DELETE", url)
        if response.status_code != 204:
            response.raise_for_status()
        return True
    except Exception as err:  # pylint: disable=broad-except
        log.error("Failed to delete secret! %s: %s", type(err).__name__, err)
        return False