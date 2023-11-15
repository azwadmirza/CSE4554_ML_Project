def showglobal(**connection_args):
    '''
    Retrieves the show global variables from the minion.

    Returns::
        show global variables full dict

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.showglobal

    '''
    mod = sys._getframe().f_code.co_name
    log.debug('{0}<--'.format(mod))
    conn = _connect(**connection_args)
    if conn is None:
        return []
    rtnv = __do_query_into_hash(conn, "SHOW GLOBAL VARIABLES")
    conn.close()
    if len(rtnv) == 0:
        rtnv.append([])

    log.debug('{0}-->{1}'.format(mod, len(rtnv[0])))
    return rtnv