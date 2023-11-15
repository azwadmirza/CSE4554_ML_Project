def _get_rest_store(store_uri, **_):
    return RestStore(partial(_get_default_host_creds, store_uri))