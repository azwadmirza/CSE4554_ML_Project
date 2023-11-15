def commit_config(module, comment=None, confirmed=False, confirm_timeout=None,
                  persist=False, check=False, label=None):
    conn = get_connection(module)
    reply = None
    try:
        if is_netconf(module):
            if check:
                reply = conn.validate()
            else:
                reply = conn.commit(confirmed=confirmed, timeout=confirm_timeout, persist=persist)
        elif is_cliconf(module):
            if check:
                module.fail_json(msg="Validate configuration is not supported with network_cli connection type")
            else:
                reply = conn.commit(comment=comment, label=label)
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))

    return reply