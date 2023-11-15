def StartSerialServer(context, identity=None, framer=ModbusAsciiFramer,
                      defer_reactor_run=False, custom_functions=[], **kwargs):
    """
    Helper method to start the Modbus Async Serial server

    :param context: The server data context
    :param identify: The server identity to use (default empty)
    :param framer: The framer to use (default ModbusAsciiFramer)
    :param port: The serial port to attach to
    :param baudrate: The baud rate to use for the serial device
    :param console: A flag indicating if you want the debug console
    :param ignore_missing_slaves: True to not send errors on a request to a
           missing slave
    :param defer_reactor_run: True/False defer running reactor.run() as part
           of starting server, to be explictly started by the user
    :param custom_functions: An optional list of custom function classes
        supported by server instance.

    """
    from twisted.internet import reactor
    from twisted.internet.serialport import SerialPort

    port = kwargs.get('port', '/dev/ttyS0')
    baudrate = kwargs.get('baudrate', Defaults.Baudrate)
    console = kwargs.get('console', False)
    bytesize = kwargs.get("bytesize", Defaults.Bytesize)
    stopbits = kwargs.get("stopbits", Defaults.Stopbits)
    parity = kwargs.get("parity", Defaults.Parity)
    timeout = kwargs.get("timeout", 0)
    xonxoff = kwargs.get("xonxoff", 0)
    rtscts = kwargs.get("rtscts", 0)

    _logger.info("Starting Modbus Serial Server on %s" % port)
    factory = ModbusServerFactory(context, framer, identity, **kwargs)
    for f in custom_functions:
        factory.decoder.register(f)
    if console:
        InstallManagementConsole({'factory': factory})
    if console:
        InstallManagementConsole({'factory': factory})

    protocol = factory.buildProtocol(None)
    SerialPort.getHost = lambda self: port  # hack for logging
    SerialPort(protocol, port, reactor, baudrate=baudrate, parity=parity,
               stopbits=stopbits, timeout=timeout, xonxoff=xonxoff,
               rtscts=rtscts, bytesize=bytesize)
    if not defer_reactor_run:
        reactor.run(installSignalHandlers=_is_main_thread())