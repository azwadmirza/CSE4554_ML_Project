def find(collection, query=None, user=None, password=None,
         host=None, port=None, database='admin'):
    """
    Find an object or list of objects in a collection

    CLI Example:

    .. code-block:: bash

        salt '*' mongodb.find mycollection '[{"foo": "FOO", "bar": "BAR"}]' <user> <password> <host> <port> <database>

    """
    conn = _connect(user, password, host, port, database)
    if not conn:
        return 'Failed to connect to mongo database'

    try:
        query = _to_dict(query)
    except Exception as err:
        return err

    try:
        log.info("Searching for %r in %s", query, collection)
        mdb = pymongo.database.Database(conn, database)
        col = getattr(mdb, collection)
        ret = col.find(query)
        return list(ret)
    except pymongo.errors.PyMongoError as err:
        log.error("Searching objects failed with error: %s", err)
        return err