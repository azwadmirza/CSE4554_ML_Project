def main():

    module = AnsibleModule(
        argument_spec=dict(
            parameter=dict(required=True, aliases=['name']),
            value=dict(default=None),
            db=dict(default=None),
            cluster=dict(default='localhost'),
            port=dict(default='5433'),
            login_user=dict(default='dbadmin'),
            login_password=dict(default=None, no_log=True),
        ), supports_check_mode = True)

    if not pyodbc_found:
        module.fail_json(msg="The python pyodbc module is required.")

    parameter_name = module.params['parameter']
    current_value = module.params['value']
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
        configuration_facts = get_configuration_facts(cursor)
        if module.check_mode:
            changed = not check(configuration_facts, parameter_name, current_value)
        else:
            try:
                changed = present(configuration_facts, cursor, parameter_name, current_value)
            except pyodbc.Error:
                e = get_exception()
                module.fail_json(msg=str(e))
    except NotSupportedError:
        e = get_exception()
        module.fail_json(msg=str(e), ansible_facts={'vertica_configuration': configuration_facts})
    except CannotDropError:
        e = get_exception()
        module.fail_json(msg=str(e), ansible_facts={'vertica_configuration': configuration_facts})
    except SystemExit:
        # avoid catching this on python 2.4
        raise
    except Exception:
        e = get_exception()
        module.fail_json(msg=e)

    module.exit_json(changed=changed, parameter=parameter_name, ansible_facts={'vertica_configuration': configuration_facts})