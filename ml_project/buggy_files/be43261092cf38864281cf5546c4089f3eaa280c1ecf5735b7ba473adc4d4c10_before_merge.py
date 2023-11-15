def async_io_factory(port=None, framer=None, **kwargs):
    """
    Factory to create asyncio based asynchronous serial clients
    :param port:  Serial port
    :param framer: Modbus Framer
    :param kwargs: Serial port options
    :return: asyncio event loop and serial client
    """
    import asyncio
    from pymodbus.client.asynchronous.asyncio import (ModbusClientProtocol,
                                                      AsyncioModbusSerialClient)
    loop = kwargs.pop("loop", None) or asyncio.get_event_loop()
    proto_cls = kwargs.pop("proto_cls", None) or ModbusClientProtocol

    try:
        from serial_asyncio import create_serial_connection
    except ImportError:
        LOGGER.critical("pyserial-asyncio is not installed, "
                        "install with 'pip install pyserial-asyncio")
        import sys
        sys.exit(1)

    client = AsyncioModbusSerialClient(port, proto_cls, framer, loop, **kwargs)
    coro = client.connect()
    if loop.is_running():
        future = asyncio.run_coroutine_threadsafe(coro, loop=loop)
        future.result()
    else:
        loop.run_until_complete(coro)
    return loop, client