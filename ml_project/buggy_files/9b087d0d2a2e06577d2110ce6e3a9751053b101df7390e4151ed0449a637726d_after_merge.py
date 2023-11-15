def get_config(module, config_filter=None, source='running'):
    conn = get_connection(module)

    # Note: Does not cache config in favour of latest config on every get operation.
    try:
        if is_netconf(module):
            out = to_xml(conn.get_config(source=source, filter=config_filter))
        elif is_cliconf(module):
            out = conn.get_config(source=source, flags=config_filter)
        cfg = out.strip()
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))
    return cfg