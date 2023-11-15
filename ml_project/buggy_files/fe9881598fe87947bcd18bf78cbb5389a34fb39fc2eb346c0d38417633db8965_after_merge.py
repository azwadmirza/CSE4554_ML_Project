def run_serial_forwarder():
    # ----------------------------------------------------------------------- #
    # initialize the datastore(serial client)
    # Note this would send the requests on the serial client with address = 0

    # ----------------------------------------------------------------------- #
    client = ModbusClient(method='rtu', port='/tmp/ptyp0')
    # If required to communicate with a specified client use unit=<unit_id>
    # in RemoteSlaveContext
    # For e.g to forward the requests to slave with unit address 1 use
    # store = RemoteSlaveContext(client, unit=1)
    store = RemoteSlaveContext(client)
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    StartServer(context, address=("localhost", 5020))