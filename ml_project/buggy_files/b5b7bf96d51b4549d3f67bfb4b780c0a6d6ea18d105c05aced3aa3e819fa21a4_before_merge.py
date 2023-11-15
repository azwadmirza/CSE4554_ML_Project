def has_default_privileges(name,
        object_name,
        object_type,
        defprivileges=None,
        grant_option=None,
        prepend='public',
        maintenance_db=None,
        user=None,
        host=None,
        port=None,
        password=None,
        runas=None):
    '''
    .. versionadded:: 2019.0.0

    Check if a role has the specified privileges on an object

    CLI Example:

    .. code-block:: bash

        salt '*' postgres.has_default_privileges user_name table_name table \\
        SELECT,INSERT maintenance_db=db_name

    name
       Name of the role whose privileges should be checked on object_type

    object_name
       Name of the object on which the check is to be performed

    object_type
       The object type, which can be one of the following:

       - table
       - sequence
       - schema
       - group
       - function

    privileges
       Comma separated list of privileges to check, from the list below:

       - INSERT
       - CREATE
       - TRUNCATE
       - TRIGGER
       - SELECT
       - USAGE
       - UPDATE
       - EXECUTE
       - REFERENCES
       - DELETE
       - ALL

    grant_option
        If grant_option is set to True, the grant option check is performed

    prepend
        Table and Sequence object types live under a schema so this should be
        provided if the object is not under the default `public` schema

    maintenance_db
        The database to connect to

    user
        database username if different from config or default

    password
        user password if any password for a specified user

    host
        Database host if different from config or default

    port
        Database port if different from config or default

    runas
        System user all operations should be performed on behalf of
    '''
    object_type, defprivileges, _defprivs = _mod_defpriv_opts(object_type, defprivileges)

    _validate_default_privileges(object_type, _defprivs, defprivileges)

    if object_type != 'group':
        owner = _get_object_owner(object_name, object_type, prepend=prepend,
            maintenance_db=maintenance_db, user=user, host=host, port=port,
            password=password, runas=runas)
        if owner is not None and name == owner:
            return True

    _defprivileges = default_privileges_list(object_name, object_type, prepend=prepend,
        maintenance_db=maintenance_db, user=user, host=host, port=port,
        password=password, runas=runas)

    if name in _defprivileges:
        if object_type == 'group':
            if grant_option:
                retval = _defprivileges[name]
            else:
                retval = True
            return retval
        else:
            _defperms = _DEFAULT_PRIVILEGE_TYPE_MAP[object_type]
            if grant_option:
                defperms = dict((_DEFAULT_PRIVILEGES_MAP[defperm], True) for defperm in _defperms)
                retval = defperms == _defprivileges[name]
            else:
                defperms = [_DEFAULT_PRIVILEGES_MAP[defperm] for defperm in _defperms]
                if 'ALL' in _defprivs:
                    retval = defperms.sort() == _defprivileges[name].keys().sort()
                else:
                    retval = set(_defprivs).issubset(
                        set(_defprivileges[name].keys()))
            return retval

    return False