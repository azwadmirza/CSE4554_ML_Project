def ext_pillar(
    minion_id,  # pylint: disable=W0613
    pillar,  # pylint: disable=W0613
    conf,
    nesting_key=None,
):
    """
    Get pillar data from Vault for the configuration ``conf``.
    """
    comps = conf.split()

    paths = [comp for comp in comps if comp.startswith("path=")]
    if not paths:
        log.error('"%s" is not a valid Vault ext_pillar config', conf)
        return {}

    vault_pillar = {}

    try:
        path = paths[0].replace("path=", "")
        path = path.format(**{"minion": minion_id})
        version2 = __utils__["vault.is_v2"](path)
        if version2["v2"]:
            path = version2["data"]

        url = "v1/{0}".format(path)
        response = __utils__["vault.make_request"]("GET", url)
        if response.status_code == 200:
            vault_pillar = response.json().get("data", {})
        else:
            log.info("Vault secret not found for: %s", path)
    except KeyError:
        log.error("No such path in Vault: %s", path)

    if nesting_key:
        vault_pillar = {nesting_key: vault_pillar}
    return vault_pillar