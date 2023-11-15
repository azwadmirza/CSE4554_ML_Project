def check_http_service(endpoint):
    if endpoint.family == socket.AF_INET:
        url = "http://{host}:{port}/health".format(
            host=endpoint.address.host, port=endpoint.address.port)
    elif endpoint.family == socket.AF_UNIX:
        quoted_path = urllib.quote(endpoint.address, safe="")
        url = "http+unix://{path}/health".format(path=quoted_path)
    else:
        raise ValueError("unrecognized socket family %r" % endpoint.family)

    session = requests.Session()
    add_unix_socket_support(session)
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    response.json()