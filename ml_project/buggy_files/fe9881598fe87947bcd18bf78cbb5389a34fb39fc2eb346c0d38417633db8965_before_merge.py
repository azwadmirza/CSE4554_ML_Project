def run_serial_forwarder():
    # ----------------------------------------------------------------------- #
    # initialize the datastore(serial client)
    # ----------------------------------------------------------------------- #
    client = ModbusClient(method='rtu', port='/dev/ptyp0')
    store = RemoteSlaveContext(client)
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    StartServer(context, address=("localhost", 5020))