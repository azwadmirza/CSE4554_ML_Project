def main():

    module = AnsibleModule(
        argument_spec=dict(
            schema=dict(required=True, aliases=['name']),
            usage_roles=dict(default=None, aliases=['usage_role']),
            create_roles=dict(default=None, aliases=['create_role']),
            owner=dict(default=None),
            state=dict(default='present', choices=['absent', 'present']),
            db=dict(default=None),
            cluster=dict(default='localhost'),
            port=dict(default='5433'),
            login_user=dict(default='dbadmin'),
            login_password=dict(default=None, no_log=True),
        ), supports_check_mode = True)

    if not pyodbc_found:
        module.fail_json(msg="The python pyodbc module is required.")

    schema = module.params['schema']
    usage_roles = []
    if module.params['usage_roles']:
        usage_roles = module.params['usage_roles'].split(',')
        usage_roles = filter(None, usage_roles)
    create_roles = []
    if module.params['create_roles']:
        create_roles = module.params['create_roles'].split(',')
        create_roles = filter(None, create_roles)
    owner = module.params['owner']
    state = module.params['state']
    db = ''
    if module.params['db']:
        db = module.params['db']

    changed = False

    try:
        dsn = (
            "Driver=Vertica;"
            "Server={0};"
            "Port={1};"
            "Database={2};"
            "User={3};"
            "Password={4};"
            "ConnectionLoadBalance={5}"
            ).format(module.params['cluster'], module.params['port'], db,
                module.params['login_user'], module.params['login_password'], 'true')
        db_conn = pyodbc.connect(dsn, autocommit=True)
        cursor = db_conn.cursor()
    except Exception:
        e = get_exception()
        module.fail_json(msg="Unable to connect to database: {0}.".format(e))

    try:
        schema_facts = get_schema_facts(cursor)
        if module.check_mode:
            changed = not check(schema_facts, schema, usage_roles, create_roles, owner)
        elif state == 'absent':
            try:
                changed = absent(schema_facts, cursor, schema, usage_roles, create_roles)
            except pyodbc.Error:
                e = get_exception()
                module.fail_json(msg=str(e))
        elif state == 'present':
            try:
                changed = present(schema_facts, cursor, schema, usage_roles, create_roles, owner)
            except pyodbc.Error:
                e = get_exception()
                module.fail_json(msg=str(e))
    except NotSupportedError:
        e = get_exception()
        module.fail_json(msg=str(e), ansible_facts={'vertica_schemas': schema_facts})
    except CannotDropError:
        e = get_exception()
        module.fail_json(msg=str(e), ansible_facts={'vertica_schemas': schema_facts})
    except SystemExit:
        # avoid catching this on python 2.4
        raise
    except Exception:
        e = get_exception()
        module.fail_json(msg=e)

    module.exit_json(changed=changed, schema=schema, ansible_facts={'vertica_schemas': schema_facts})