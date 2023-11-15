def free_slave(**connection_args):
    '''
    Frees a slave from its master.  This is a WIP, do not use.

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.free_slave
    '''
    slave_db = _connect(**connection_args)
    slave_cur = slave_db.cursor(MySQLdb.cursors.DictCursor)
    slave_cur.execute('show slave status')
    slave_status = slave_cur.fetchone()
    master = {'host': slave_status['Master_Host']}

    try:
        # Try to connect to the master and flush logs before promoting to
        # master.  This may fail if the master is no longer available.
        # I am also assuming that the admin password is the same on both
        # servers here, and only overriding the host option in the connect
        # function.
        master_db = _connect(**master)
        master_cur = master_db.cursor()
        master_cur.execute('flush logs')
        master_db.close()
    except MySQLdb.OperationalError:
        pass

    slave_cur.execute('stop slave')
    slave_cur.execute('reset master')
    slave_cur.execute('change master to MASTER_HOST=''')
    slave_cur.execute('show slave status')
    results = slave_cur.fetchone()

    if results is None:
        return 'promoted'
    else:
        return 'failed'