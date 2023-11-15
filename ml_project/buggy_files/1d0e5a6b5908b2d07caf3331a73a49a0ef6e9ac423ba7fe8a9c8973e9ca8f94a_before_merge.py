def run_commands(module, commands, check_rc=True):
    connection = get_connection(module)
    try:
        out = connection.run_commands(commands=commands, check_rc=check_rc)
        return out
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))