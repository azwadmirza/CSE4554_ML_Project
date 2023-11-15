def _get_serv(ret=None, commit=False):
    '''
    Return a mysql cursor
    '''
    _options = _get_options(ret)
    conn = MySQLdb.connect(host=_options.get('host'),
                           user=_options.get('user'),
                           passwd=_options.get('pass'),
                           db=_options.get('db'),
                           port=_options.get('port'))
    cursor = conn.cursor()
    try:
        yield cursor
    except MySQLdb.DatabaseError as err:
        error = err.args
        sys.stderr.write(str(error))
        cursor.execute("ROLLBACK")
        raise err
    else:
        if commit:
            cursor.execute("COMMIT")
        else:
            cursor.execute("ROLLBACK")
    finally:
        conn.close()