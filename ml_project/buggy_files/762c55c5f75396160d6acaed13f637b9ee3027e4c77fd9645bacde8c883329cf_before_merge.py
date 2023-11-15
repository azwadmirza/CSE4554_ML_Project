def remove(collection, query=None, user=None, password=None,
           host=None, port=None, database='admin', w=1):
    """
    Remove an object or list of objects into a collection

    CLI Example:

    .. code-block:: bash

        salt '*' mongodb.remove mycollection '[{"foo": "FOO", "bar": "BAR"}, {"foo": "BAZ", "bar": "BAM"}]' <user> <password> <host> <port> <database>

    """
    conn = _connect(user, password, host, port, database)
    if not conn:
        return 'Failed to connect to mongo database'

    try:
        query = _to_dict(query)
    except Exception as err:
        return err.message

    try:
        log.info("Removing %r from %s", query, collection)
        mdb = pymongo.database.Database(conn, database)
        col = getattr(mdb, collection)
        ret = col.remove(query, w=w)
        return "{0} objects removed".format(ret['n'])
    except pymongo.errors.PyMongoError as err:
        log.error("Removing objects failed with error: %s", err.message)
        return err.message