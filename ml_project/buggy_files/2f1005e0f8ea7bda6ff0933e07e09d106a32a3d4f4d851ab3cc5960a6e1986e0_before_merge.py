def _role_cmd_args(name,
                   sub_cmd='',
                   typ_='role',
                   encrypted=None,
                   login=None,
                   connlimit=None,
                   inherit=None,
                   createdb=None,
                   createuser=None,
                   createroles=None,
                   superuser=None,
                   groups=None,
                   replication=None,
                   rolepassword=None,
                   db_role=None):
    if createuser is not None and superuser is None:
        superuser = createuser
    if inherit is None:
        if typ_ in ['user', 'group']:
            inherit = True
    if login is None:
        if typ_ == 'user':
            login = True
        if typ_ == 'group':
            login = False
    # defaults to encrypted passwords (md5{password}{rolename})
    if encrypted is None:
        encrypted = _DEFAULT_PASSWORDS_ENCRYPTION
    skip_passwd = False
    escaped_password = ''
    if not (
        rolepassword is not None
        # first is passwd set
        # second is for handling NOPASSWD
        and (
            isinstance(rolepassword, six.string_types) and bool(rolepassword)
        )
        or (
            isinstance(rolepassword, bool)
        )
    ):
        skip_passwd = True
    if isinstance(rolepassword, six.string_types) and bool(rolepassword):
        escaped_password = '{0!r}'.format(
            _maybe_encrypt_password(name,
                                    rolepassword.replace('\'', '\'\''),
                                    encrypted=encrypted))
    skip_superuser = False
    if bool(db_role) and bool(superuser) == bool(db_role['superuser']):
        skip_superuser = True
    flags = (
        {'flag': 'INHERIT', 'test': inherit},
        {'flag': 'CREATEDB', 'test': createdb},
        {'flag': 'CREATEROLE', 'test': createroles},
        {'flag': 'SUPERUSER', 'test': superuser,
         'skip': skip_superuser},
        {'flag': 'REPLICATION', 'test': replication},
        {'flag': 'LOGIN', 'test': login},
        {'flag': 'CONNECTION LIMIT',
         'test': bool(connlimit),
         'addtxt': str(connlimit),
         'skip': connlimit is None},
        {'flag': 'ENCRYPTED',
         'test': (encrypted is not None and bool(rolepassword)),
         'skip': skip_passwd or isinstance(rolepassword, bool),
         'cond': encrypted,
         'prefix': 'UN'},
        {'flag': 'PASSWORD', 'test': bool(rolepassword),
         'skip': skip_passwd,
         'addtxt': escaped_password},
    )
    for data in flags:
        sub_cmd = _add_role_flag(sub_cmd, **data)
    if sub_cmd.endswith('WITH'):
        sub_cmd = sub_cmd.replace(' WITH', '')
    if groups:
        for group in groups.split(','):
            sub_cmd = '{0}; GRANT "{1}" TO "{2}"'.format(sub_cmd, group, name)
    return sub_cmd