def tcp(ctx, host, port, framer):
    from pymodbus.repl.client import ModbusTcpClient
    kwargs = dict(host=host, port=port)
    if framer == 'rtu':
        from pymodbus.framer.rtu_framer import ModbusRtuFramer
        kwargs['framer'] = ModbusRtuFramer
    client = ModbusTcpClient(**kwargs)
    cli(client)