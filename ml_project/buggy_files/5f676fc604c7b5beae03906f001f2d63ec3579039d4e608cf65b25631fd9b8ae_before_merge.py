def commit_config(module, comment=None, confirmed=False, confirm_timeout=None,
                  persist=False, check=False, label=None):
    conn = get_connection(module)
    reply = None
    try:
        if check:
            reply = conn.validate()
        else:
            if is_netconf(module):
                reply = conn.commit(confirmed=confirmed, timeout=confirm_timeout, persist=persist)
            elif is_cliconf(module):
                reply = conn.commit(comment=comment, label=label)
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))

    return reply