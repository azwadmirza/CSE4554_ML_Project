def run_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #
    store = ModbusSlaveContext()
    context = ModbusServerContext(slaves=store, single=True)
    
    # ----------------------------------------------------------------------- # 
    # initialize the server information
    # ----------------------------------------------------------------------- # 
    # If you don't set this or any fields, they are defaulted to empty strings.
    # ----------------------------------------------------------------------- # 
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = '1.5'

    # ----------------------------------------------------------------------- #
    # Add an example which is long enough to force the ReadDeviceInformation
    # request / response to require multiple responses to send back all of the
    # information.
    # ----------------------------------------------------------------------- #

    identity[0x80] = "Lorem ipsum dolor sit amet, consectetur adipiscing " \
                     "elit. Vivamus rhoncus massa turpis, sit amet " \
                     "ultrices orci semper ut. Aliquam tristique sapien in " \
                     "lacus pharetra, in convallis nunc consectetur. Nunc " \
                     "velit elit, vehicula tempus tempus sed. "

    # ----------------------------------------------------------------------- #
    # Add an example with repeated object IDs. The MODBUS specification is
    # entirely silent on whether or not this is allowed. In practice, this
    # should be assumed to be contrary to the MODBUS specification and other
    # clients (other than pymodbus) might behave differently when presented
    # with an object ID occurring twice in the returned information.
    #
    # Use this at your discretion, and at the very least ensure that all
    # objects which share a single object ID can fit together within a single
    # ADU unit. In the case of Modbus RTU, this is about 240 bytes or so. In
    # other words, when the spec says "An object is indivisible, therefore
    # any object must have a size consistent with the size of transaction
    # response", if you use repeated OIDs, apply that rule to the entire
    # grouping of objects with the repeated OID.
    # ----------------------------------------------------------------------- #
    identity[0x81] = ['pymodbus {0}'.format(pymodbus_version),
                      'pyserial {0}'.format(pyserial_version)]

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- # 
    # Tcp:
    StartTcpServer(context, identity=identity, address=("localhost", 5020))