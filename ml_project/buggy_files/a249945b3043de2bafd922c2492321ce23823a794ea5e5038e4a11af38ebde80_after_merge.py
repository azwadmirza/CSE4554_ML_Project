def StartTcpServer(context, identity=None, address=None,
                   console=False, defer_reactor_run=False, custom_functions=[],
                   **kwargs):
    """
    Helper method to start the Modbus Async TCP server

    :param context: The server data context
    :param identify: The server identity to use (default empty)
    :param address: An optional (interface, port) to bind to.
    :param console: A flag indicating if you want the debug console
    :param ignore_missing_slaves: True to not send errors on a request \
    to a missing slave
    :param defer_reactor_run: True/False defer running reactor.run() as part \
    of starting server, to be explictly started by the user
    :param custom_functions: An optional list of custom function classes
        supported by server instance.
    """
    from twisted.internet import reactor

    address = address or ("", Defaults.Port)
    framer = kwargs.pop("framer", ModbusSocketFramer)
    factory = ModbusServerFactory(context, framer, identity, **kwargs)
    for f in custom_functions:
        factory.decoder.register(f)
    if console:
        InstallManagementConsole({'factory': factory})

    _logger.info("Starting Modbus TCP Server on %s:%s" % address)
    reactor.listenTCP(address[1], factory, interface=address[0])
    if not defer_reactor_run:
        reactor.run(installSignalHandlers=_is_main_thread())