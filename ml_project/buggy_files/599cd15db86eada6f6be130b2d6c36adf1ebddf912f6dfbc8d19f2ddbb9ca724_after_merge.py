def present(dbname, name,
            owner=None, user=None,
            db_user=None, db_password=None,
            db_host=None, db_port=None):
    '''
    Ensure that the named schema is present in the database.

    dbname
        The database's name will work on

    name
        The name of the schema to manage

    user
        system user all operations should be performed on behalf of

    db_user
        database username if different from config or default

    db_password
        user password if any password for a specified user

    db_host
        Database host if different from config or default

    db_port
        Database port if different from config or default
    '''
    ret = {'dbname': dbname,
           'name': name,
           'changes': {},
           'result': True,
           'comment': 'Schema {0} is already present in '
                      'database {1}'.format(name, dbname)}

    db_args = {
        'db_user': db_user,
        'db_password': db_password,
        'db_host': db_host,
        'db_port': db_port,
        'user': user
    }

    # check if schema exists
    schema_attr = __salt__['postgres.schema_get'](dbname, name, **db_args)

    cret = None

    # The schema is not present, make it!
    if schema_attr is None:
        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'Schema {0} is set to be created' \
                             ' in database {1}.'.format(name, dbname)
            return ret
        cret = __salt__['postgres.schema_create'](dbname,
                                                  name,
                                                  owner=owner,
                                                  **db_args)
    else:
        msg = 'Schema {0} already exists in database {1}'
        cret = None

    if cret:
        msg = 'Schema {0} has been created in database {1}'
        ret['result'] = True
        ret['changes'][name] = 'Present'
    elif cret is not None:
        msg = 'Failed to create schema {0} in database {1}'
        ret['result'] = False
    else:
        msg = 'Schema {0} already exists in database {1}'
        ret['result'] = True

    ret['comment'] = msg.format(name, dbname)
    return ret