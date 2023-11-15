def main():

    module = AnsibleModule(
        argument_spec=dict(
            user=dict(required=True, aliases=['name']),
            profile=dict(default=None),
            resource_pool=dict(default=None),
            password=dict(default=None, no_log=True),
            expired=dict(type='bool', default=None),
            ldap=dict(type='bool', default=None),
            roles=dict(default=None, aliases=['role']),
            state=dict(default='present', choices=['absent', 'present', 'locked']),
            db=dict(default=None),
            cluster=dict(default='localhost'),
            port=dict(default='5433'),
            login_user=dict(default='dbadmin'),
            login_password=dict(default=None, no_log=True),
        ), supports_check_mode = True)

    if not pyodbc_found:
        module.fail_json(msg="The python pyodbc module is required.")

    user = module.params['user']
    profile = module.params['profile']
    if profile:
        profile = profile.lower()
    resource_pool = module.params['resource_pool']
    if resource_pool:
        resource_pool = resource_pool.lower()
    password = module.params['password']
    expired = module.params['expired']
    ldap = module.params['ldap']
    roles = []
    if module.params['roles']:
        roles = module.params['roles'].split(',')
        roles = filter(None, roles)
    state = module.params['state']
    if state == 'locked':
        locked = True
    else:
        locked = False
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
        user_facts = get_user_facts(cursor)
        if module.check_mode:
            changed = not check(user_facts, user, profile, resource_pool,
                locked, password, expired, ldap, roles)
        elif state == 'absent':
            try:
                changed = absent(user_facts, cursor, user, roles)
            except pyodbc.Error:
                e = get_exception()
                module.fail_json(msg=str(e))
        elif state in ['present', 'locked']:
            try:
                changed = present(user_facts, cursor, user, profile, resource_pool,
                    locked, password, expired, ldap, roles)
            except pyodbc.Error:
                e = get_exception()
                module.fail_json(msg=str(e))
    except NotSupportedError:
        e = get_exception()
        module.fail_json(msg=str(e), ansible_facts={'vertica_users': user_facts})
    except CannotDropError:
        e = get_exception()
        module.fail_json(msg=str(e), ansible_facts={'vertica_users': user_facts})
    except SystemExit:
        # avoid catching this on python 2.4
        raise
    except Exception:
        e = get_exception()
        module.fail_json(msg=to_native(e))

    module.exit_json(changed=changed, user=user, ansible_facts={'vertica_users': user_facts})