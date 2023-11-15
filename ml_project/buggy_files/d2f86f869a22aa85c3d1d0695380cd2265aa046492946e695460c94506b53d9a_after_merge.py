def main():

    module = AnsibleModule(
        argument_spec=dict(
            role=dict(required=True, aliases=['name']),
            assigned_roles=dict(default=None, aliases=['assigned_role']),
            state=dict(default='present', choices=['absent', 'present']),
            db=dict(default=None),
            cluster=dict(default='localhost'),
            port=dict(default='5433'),
            login_user=dict(default='dbadmin'),
            login_password=dict(default=None, no_log=True),
        ), supports_check_mode = True)

    if not pyodbc_found:
        module.fail_json(msg="The python pyodbc module is required.")

    role = module.params['role']
    assigned_roles = []
    if module.params['assigned_roles']:
        assigned_roles = module.params['assigned_roles'].split(',')
        assigned_roles = filter(None, assigned_roles)
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
        role_facts = get_role_facts(cursor)
        if module.check_mode:
            changed = not check(role_facts, role, assigned_roles)
        elif state == 'absent':
            try:
                changed = absent(role_facts, cursor, role, assigned_roles)
            except pyodbc.Error:
                e = get_exception()
                module.fail_json(msg=str(e))
        elif state == 'present':
            try:
                changed = present(role_facts, cursor, role, assigned_roles)
            except pyodbc.Error:
                e = get_exception()
                module.fail_json(msg=str(e))
    except NotSupportedError:
        e = get_exception()
        module.fail_json(msg=str(e), ansible_facts={'vertica_roles': role_facts})
    except CannotDropError:
        e = get_exception()
        module.fail_json(msg=str(e), ansible_facts={'vertica_roles': role_facts})
    except SystemExit:
        # avoid catching this on python 2.4
        raise
    except Exception:
        e = get_exception()
        module.fail_json(msg=to_native(e))

    module.exit_json(changed=changed, role=role, ansible_facts={'vertica_roles': role_facts})