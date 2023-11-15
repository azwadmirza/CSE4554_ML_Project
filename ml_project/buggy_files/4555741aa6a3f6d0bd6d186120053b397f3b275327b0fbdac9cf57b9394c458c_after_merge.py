def discard_changes(module):
    conn = get_connection(module)
    return conn.discard_changes()