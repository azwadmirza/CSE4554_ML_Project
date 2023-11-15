def main():
    module = AnsibleModule(
        argument_spec = dict(
            database=dict(required=True, aliases=['db']),
            state=dict(default='present', choices=['present', 'absent']),
            privs=dict(required=False, aliases=['priv']),
            type=dict(default='table',
                      choices=['table',
                               'sequence',
                               'function',
                               'database',
                               'schema',
                               'language',
                               'tablespace',
                               'group']),
            objs=dict(required=False, aliases=['obj']),
            schema=dict(required=False),
            roles=dict(required=True, aliases=['role']),
            grant_option=dict(required=False, type='bool',
                              aliases=['admin_option']),
            host=dict(default='', aliases=['login_host']),
            port=dict(type='int', default=5432),
            unix_socket=dict(default='', aliases=['login_unix_socket']),
            login=dict(default='postgres', aliases=['login_user']),
            password=dict(default='', aliases=['login_password'], no_log=True),
            ssl_mode=dict(default="prefer", choices=['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']),
            ssl_rootcert=dict(default=None)
        ),
        supports_check_mode = True
    )

    # Create type object as namespace for module params
    p = type('Params', (), module.params)

    # param "schema": default, allowed depends on param "type"
    if p.type in ['table', 'sequence', 'function']:
        p.schema = p.schema or 'public'
    elif p.schema:
        module.fail_json(msg='Argument "schema" is not allowed '
                             'for type "%s".' % p.type)

    # param "objs": default, required depends on param "type"
    if p.type == 'database':
        p.objs = p.objs or p.database
    elif not p.objs:
        module.fail_json(msg='Argument "objs" is required '
                             'for type "%s".' % p.type)

    # param "privs": allowed, required depends on param "type"
    if p.type == 'group':
        if p.privs:
            module.fail_json(msg='Argument "privs" is not allowed '
                                 'for type "group".')
    elif not p.privs:
        module.fail_json(msg='Argument "privs" is required '
                             'for type "%s".' % p.type)

    # Connect to Database
    if not psycopg2:
        module.fail_json(msg='Python module "psycopg2" must be installed.')
    try:
        conn = Connection(p)
    except psycopg2.Error as e:
        module.fail_json(msg='Could not connect to database: %s' % to_native(e), exception=traceback.format_exc())
    except TypeError as e:
        if 'sslrootcert' in e.args[0]:
            module.fail_json(msg='Postgresql server must be at least version 8.4 to support sslrootcert')
        module.fail_json(msg="unable to connect to database: %s" % to_native(e), exception=traceback.format_exc())
    except ValueError as e:
        # We raise this when the psycopg library is too old
        module.fail_json(msg=to_native(e))

    try:
        # privs
        if p.privs:
            privs = frozenset(pr.upper() for pr in p.privs.split(','))
            if not privs.issubset(VALID_PRIVS):
                module.fail_json(msg='Invalid privileges specified: %s' % privs.difference(VALID_PRIVS))
        else:
            privs = None

        # objs:
        if p.type == 'table' and p.objs == 'ALL_IN_SCHEMA':
            objs = conn.get_all_tables_in_schema(p.schema)
        elif p.type == 'sequence' and p.objs == 'ALL_IN_SCHEMA':
            objs = conn.get_all_sequences_in_schema(p.schema)
        else:
            objs = p.objs.split(',')

        # function signatures are encoded using ':' to separate args
        if p.type == 'function':
            objs = [obj.replace(':', ',') for obj in objs]

        # roles
        if p.roles == 'PUBLIC':
            roles = 'PUBLIC'
        else:
            roles = p.roles.split(',')

        changed = conn.manipulate_privs(
            obj_type = p.type,
            privs = privs,
            objs = objs,
            roles = roles,
            state = p.state,
            grant_option = p.grant_option,
            schema_qualifier=p.schema
        )

    except Error as e:
        conn.rollback()
        module.fail_json(msg=e.message, exception=traceback.format_exc())

    except psycopg2.Error as e:
        conn.rollback()
        # psycopg2 errors come in connection encoding
        msg = to_text(e.message(encoding=conn.encoding))
        module.fail_json(msg=msg)

    if module.check_mode:
        conn.rollback()
    else:
        conn.commit()
    module.exit_json(changed=changed)