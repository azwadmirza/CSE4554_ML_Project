def absent(dbname, name, user=None,
           db_user=None, db_password=None,
           db_host=None, db_port=None):
    '''
    Ensure that the named schema is absent.

    dbname
        The database's name will work on

    name
        The name of the schema to remove

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
    ret = {'name': name,
           'dbname': dbname,
           'changes': {},
           'result': True,
           'comment': ''}

    db_args = {
        'db_user': db_user,
        'db_password': db_password,
        'db_host': db_host,
        'db_port': db_port,
        'user': user
        }

    # check if schema exists and remove it
    if __salt__['postgres.schema_exists'](dbname, name, **db_args):
        if __opts__['test']:
            ret['result'] = None
            ret['comment'] = 'Schema {0} is set to be removed' \
                             ' from database {1}'.format(name, dbname)
            return ret
        elif __salt__['postgres.schema_remove'](dbname, name, **db_args):
            ret['comment'] = 'Schema {0} has been removed' \
                             ' from database {1}'.format(name, dbname)
            ret['changes'][name] = 'Absent'
            return ret
        else:
            ret['result'] = False
            ret['comment'] = 'Schema {0} failed to be removed'.format(name)
            return ret
    else:
        ret['comment'] = 'Schema {0} is not present in database {1},' \
                         ' so it cannot be removed'.format(name, dbname)

    return ret