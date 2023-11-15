def async_io_factory(host="127.0.0.1", port=Defaults.TLSPort, sslctx=None,
                     server_hostname=None, framer=None, source_address=None,
                     timeout=None, **kwargs):
    """
    Factory to create asyncio based asynchronous tls clients
    :param host: Host IP address
    :param port: Port
    :param sslctx: The SSLContext to use for TLS (default None and auto create)
    :param server_hostname: Target server's name matched for certificate
    :param framer: Modbus Framer
    :param source_address: Bind address
    :param timeout: Timeout in seconds
    :param kwargs:
    :return: asyncio event loop and tcp client
    """
    import asyncio
    from pymodbus.client.asynchronous.async_io import init_tls_client
    loop = kwargs.get("loop") or asyncio.new_event_loop()
    proto_cls = kwargs.get("proto_cls", None)
    if not loop.is_running():
        asyncio.set_event_loop(loop)
        cor = init_tls_client(proto_cls, loop, host, port, sslctx, server_hostname,
                              framer)
        client = loop.run_until_complete(asyncio.gather(cor))[0]
    else:
        cor = init_tls_client(proto_cls, loop, host, port, sslctx, server_hostname,
                              framer)
        future = asyncio.run_coroutine_threadsafe(cor, loop=loop)
        client = future.result()

    return loop, client