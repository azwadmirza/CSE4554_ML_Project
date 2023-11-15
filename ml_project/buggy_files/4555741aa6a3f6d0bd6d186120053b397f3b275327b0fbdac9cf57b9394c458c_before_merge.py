def discard_changes(module, exit=False):
    conn = get_connection(module)
    return conn.discard_changes(exit=exit)