def tcp(ctx, host, port, framer):
    from pymodbus.repl.client import ModbusTcpClient
    broadcast = ctx.obj.get("broadcast")
    kwargs = dict(host=host, port=port, broadcast_enable=broadcast)
    if framer == 'rtu':
        from pymodbus.framer.rtu_framer import ModbusRtuFramer
        kwargs['framer'] = ModbusRtuFramer
    client = ModbusTcpClient(**kwargs)
    cli(client)