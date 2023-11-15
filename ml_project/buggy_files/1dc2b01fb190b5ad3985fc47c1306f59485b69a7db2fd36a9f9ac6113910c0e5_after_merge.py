def create_server(host, port=0, backlog=socket.SOMAXCONN, timeout=None):
    """Return a local server socket listening on the given port."""
    if host is None:
        host = "127.0.0.1"
    if port is None:
        port = 0

    try:
        server = _new_sock()
        server.bind((host, port))
        if timeout is not None:
            server.settimeout(timeout)
        server.listen(backlog)
    except Exception:
        server.close()
        raise
    return server