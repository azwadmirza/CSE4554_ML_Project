def get_master_status(**connection_args):
    '''
    Retrieves the master status from the minion.

    Returns::

        {'host.domain.com': {'Binlog_Do_DB': '',
                         'Binlog_Ignore_DB': '',
                         'File': 'mysql-bin.000021',
                         'Position': 107}}

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.get_master_status

    '''
    mod = sys._getframe().f_code.co_name
    log.debug('{0}<--'.format(mod))
    conn = _connect(**connection_args)
    if conn is None:
        return []
    rtnv = __do_query_into_hash(conn, "SHOW MASTER STATUS")
    conn.close()

    # check for if this minion is not a master
    if len(rtnv) == 0:
        rtnv.append([])

    log.debug('{0}-->{1}'.format(mod, len(rtnv[0])))
    return rtnv[0]