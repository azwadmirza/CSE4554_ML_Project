def _establish_new_socket_connection(
    session_id: str,
    server_hostname: str,
    server_port: int,
    logger: Logger,
    receive_timeout: float,
    proxy: Optional[str],
    proxy_headers: Optional[Dict[str, str]],
    trace_enabled: bool,
) -> Union[ssl.SSLSocket, Socket]:
    if proxy is not None:
        parsed_proxy = urlparse(proxy)
        proxy_host, proxy_port = parsed_proxy.hostname, parsed_proxy.port or 80
        proxy_addr = socket.getaddrinfo(
            proxy_host,
            proxy_port,
            0,
            socket.SOCK_STREAM,
            socket.SOL_TCP,
        )[0]
        sock = socket.socket(proxy_addr[0], proxy_addr[1], proxy_addr[2])
        sock.settimeout(receive_timeout)
        sock.connect(proxy_addr[4])  # proxy address
        message = [f"CONNECT {server_hostname}:{server_port} HTTP/1.0"]
        if parsed_proxy.username is not None and parsed_proxy.password is not None:
            # In the case where the proxy is "http://{username}:{password}@{hostname}:{port}"
            raw_value = f"{parsed_proxy.username}:{parsed_proxy.password}"
            auth = b64encode(raw_value.encode("utf-8")).decode("ascii")
            message.append(f"Proxy-Authorization: Basic {auth}")
        if proxy_headers is not None:
            for k, v in proxy_headers.items():
                message.append(f"{k}: {v}")
        message.append("")
        message.append("")
        req: str = "\r\n".join([line.lstrip() for line in message])
        if trace_enabled:
            logger.debug(f"Proxy connect request (session id: {session_id}):\n{req}")
        sock.send(req.encode("utf-8"))
        status, text = _parse_connect_response(sock)
        if trace_enabled:
            log_message = f"Proxy connect response (session id: {session_id}):\n{text}"
            logger.debug(log_message)
        if status != 200:
            raise Exception(
                f"Failed to connect to the proxy (proxy: {proxy}, connect status code: {status})"
            )

        sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(
            sock,
            do_handshake_on_connect=True,
            suppress_ragged_eofs=True,
            server_hostname=server_hostname,
        )
        return sock

    if server_port != 443:
        addr = socket.getaddrinfo(
            server_hostname, server_port, 0, socket.SOCK_STREAM, socket.SOL_TCP
        )[0]
        # only for library testing
        logger.info(
            f"Using non-ssl socket to connect ({server_hostname}:{server_port})"
        )
        sock = Socket(addr[0], addr[1], addr[2])
        sock.settimeout(3)
        sock.connect((server_hostname, server_port))
        return sock

    sock = Socket(type=ssl.SOCK_STREAM)
    sock = ssl.SSLContext(ssl.PROTOCOL_SSLv23).wrap_socket(
        sock,
        do_handshake_on_connect=True,
        suppress_ragged_eofs=True,
        server_hostname=server_hostname,
    )
    sock.settimeout(receive_timeout)
    sock.connect((server_hostname, server_port))
    return sock