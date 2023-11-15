def main():

    module = AnsibleModule(
        argument_spec=dict(
            cluster=dict(default='localhost'),
            port=dict(default='5433'),
            db=dict(default=None),
            login_user=dict(default='dbadmin'),
            login_password=dict(default=None, no_log=True),
        ), supports_check_mode = True)

    if not pyodbc_found:
        module.fail_json(msg="The python pyodbc module is required.")

    db = ''
    if module.params['db']:
        db = module.params['db']

    try:
        dsn = (
            "Driver=Vertica;"
            "Server=%s;"
            "Port=%s;"
            "Database=%s;"
            "User=%s;"
            "Password=%s;"
            "ConnectionLoadBalance=%s"
            ) % (module.params['cluster'], module.params['port'], db,
                module.params['login_user'], module.params['login_password'], 'true')
        db_conn = pyodbc.connect(dsn, autocommit=True)
        cursor = db_conn.cursor()
    except Exception:
        e = get_exception()
        module.fail_json(msg="Unable to connect to database: %s." % str(e))

    try:
        schema_facts = get_schema_facts(cursor)
        user_facts = get_user_facts(cursor)
        role_facts = get_role_facts(cursor)
        configuration_facts = get_configuration_facts(cursor)
        node_facts = get_node_facts(cursor)
        module.exit_json(changed=False,
            ansible_facts={'vertica_schemas': schema_facts,
                           'vertica_users': user_facts,
                           'vertica_roles': role_facts,
                           'vertica_configuration': configuration_facts,
                           'vertica_nodes': node_facts})
    except NotSupportedError:
        e = get_exception()
        module.fail_json(msg=str(e))
    except SystemExit:
        # avoid catching this on python 2.4
        raise
    except Exception:
        e = get_exception()
        module.fail_json(msg=to_native(e))