def main():
    module = AnsibleModule(
        argument_spec=dict(
            login_user=dict(default="postgres"),
            login_password=dict(default="", no_log=True),
            login_host=dict(default=""),
            login_unix_socket=dict(default=""),
            user=dict(required=True, aliases=['name']),
            password=dict(default=None, no_log=True),
            state=dict(default="present", choices=["absent", "present"]),
            priv=dict(default=None),
            db=dict(default=''),
            port=dict(default='5432'),
            fail_on_user=dict(type='bool', default='yes'),
            role_attr_flags=dict(default=''),
            encrypted=dict(type='bool', default='no'),
            no_password_changes=dict(type='bool', default='no'),
            expires=dict(default=None),
            ssl_mode=dict(default='prefer', choices=['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']),
            ssl_rootcert=dict(default=None)
        ),
        supports_check_mode=True
    )

    user = module.params["user"]
    password = module.params["password"]
    state = module.params["state"]
    fail_on_user = module.params["fail_on_user"]
    db = module.params["db"]
    if db == '' and module.params["priv"] is not None:
        module.fail_json(msg="privileges require a database to be specified")
    privs = parse_privs(module.params["priv"], db)
    no_password_changes = module.params["no_password_changes"]
    if module.params["encrypted"]:
        encrypted = "ENCRYPTED"
    else:
        encrypted = "UNENCRYPTED"
    expires = module.params["expires"]
    sslrootcert = module.params["ssl_rootcert"]

    if not postgresqldb_found:
        module.fail_json(msg="the python psycopg2 module is required")

    # To use defaults values, keyword arguments must be absent, so
    # check which values are empty and don't include in the **kw
    # dictionary
    params_map = {
        "login_host": "host",
        "login_user": "user",
        "login_password": "password",
        "port": "port",
        "db": "database",
        "ssl_mode": "sslmode",
        "ssl_rootcert": "sslrootcert"
    }
    kw = dict((params_map[k], v) for (k, v) in iteritems(module.params)
              if k in params_map and v != "" and v is not None)

    # If a login_unix_socket is specified, incorporate it here.
    is_localhost = "host" not in kw or kw["host"] == "" or kw["host"] == "localhost"
    if is_localhost and module.params["login_unix_socket"] != "":
        kw["host"] = module.params["login_unix_socket"]

    if psycopg2.__version__ < '2.4.3' and sslrootcert is not None:
        module.fail_json(msg='psycopg2 must be at least 2.4.3 in order to user the ssl_rootcert parameter')

    try:
        db_connection = psycopg2.connect(**kw)
        cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    except TypeError:
        e = get_exception()
        if 'sslrootcert' in e.args[0]:
            module.fail_json(msg='Postgresql server must be at least version 8.4 to support sslrootcert')
        module.fail_json(msg="unable to connect to database: %s" % e)

    except Exception:
        e = get_exception()
        module.fail_json(msg="unable to connect to database: %s" % e)

    try:
        role_attr_flags = parse_role_attrs(cursor, module.params["role_attr_flags"])
    except InvalidFlagsError:
        e = get_exception()
        module.fail_json(msg=str(e))

    kw = dict(user=user)
    changed = False
    user_removed = False

    if state == "present":
        if user_exists(cursor, user):
            try:
                changed = user_alter(cursor, module, user, password, role_attr_flags, encrypted, expires, no_password_changes)
            except SQLParseError:
                e = get_exception()
                module.fail_json(msg=str(e))
        else:
            try:
                changed = user_add(cursor, user, password, role_attr_flags, encrypted, expires)
            except SQLParseError:
                e = get_exception()
                module.fail_json(msg=str(e))
        try:
            changed = grant_privileges(cursor, user, privs) or changed
        except SQLParseError:
            e = get_exception()
            module.fail_json(msg=str(e))
    else:
        if user_exists(cursor, user):
            if module.check_mode:
                changed = True
                kw['user_removed'] = True
            else:
                try:
                    changed = revoke_privileges(cursor, user, privs)
                    user_removed = user_delete(cursor, user)
                except SQLParseError:
                    e = get_exception()
                    module.fail_json(msg=str(e))
                changed = changed or user_removed
                if fail_on_user and not user_removed:
                    msg = "unable to remove user"
                    module.fail_json(msg=msg)
                kw['user_removed'] = user_removed

    if changed:
        if module.check_mode:
            db_connection.rollback()
        else:
            db_connection.commit()

    kw['changed'] = changed
    module.exit_json(**kw)