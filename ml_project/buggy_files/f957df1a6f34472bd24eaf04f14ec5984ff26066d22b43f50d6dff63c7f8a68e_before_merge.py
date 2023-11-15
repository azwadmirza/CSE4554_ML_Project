def updating_writer(a):
    """ A worker process that runs every so often and
    updates live values of the context which resides in an SQLite3 database.
    It should be noted that there is a race condition for the update.
    :param arguments: The input arguments to the call
    """
    log.debug("Updating the database context")
    context  = a[0]
    readfunction = 0x03 # read holding registers
    writefunction = 0x10
    slave_id = 0x01 # slave address
    count = 50

    # import pdb; pdb.set_trace()

    rand_value = random.randint(0, 9999)
    rand_addr = random.randint(0, 65000)
    log.debug("Writing to datastore: {}, {}".format(rand_addr, rand_value))
    # import pdb; pdb.set_trace()
    context[slave_id].setValues(writefunction, rand_addr, [rand_value])
    values = context[slave_id].getValues(readfunction, rand_addr, count)
    log.debug("Values from datastore: " + str(values))