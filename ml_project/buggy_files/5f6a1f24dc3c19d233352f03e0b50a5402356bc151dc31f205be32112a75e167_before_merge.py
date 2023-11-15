def user_alter(cursor, module, user, password, role_attr_flags, encrypted, expires, no_password_changes):
    """Change user password and/or attributes. Return True if changed, False otherwise."""
    changed = False

    # Note: role_attr_flags escaped by parse_role_attrs and encrypted is a literal
    if user == 'PUBLIC':
        if password is not None:
            module.fail_json(msg="cannot change the password for PUBLIC user")
        elif role_attr_flags != '':
            module.fail_json(msg="cannot change the role_attr_flags for PUBLIC user")
        else:
            return False

    # Handle passwords.
    if not no_password_changes and (password is not None or role_attr_flags != '' or expires is not None):
        # Select password and all flag-like columns in order to verify changes.
        select = "SELECT * FROM pg_authid where rolname=%(user)s"
        cursor.execute(select, {"user": user})
        # Grab current role attributes.
        current_role_attrs = cursor.fetchone()

        # Do we actually need to do anything?
        pwchanging = False
        if password is not None:
            # 32: MD5 hashes are represented as a sequence of 32 hexadecimal digits
            #  3: The size of the 'md5' prefix
            # When the provided password looks like a MD5-hash, value of
            # 'encrypted' is ignored.
            if ((password.startswith('md5') and len(password) == 32 + 3) or encrypted == 'UNENCRYPTED'):
                if password != current_role_attrs['rolpassword']:
                    pwchanging = True
            elif encrypted == 'ENCRYPTED':
                hashed_password = 'md5{0}'.format(md5(to_bytes(password) + to_bytes(user)).hexdigest())
                if hashed_password != current_role_attrs['rolpassword']:
                    pwchanging = True

        role_attr_flags_changing = False
        if role_attr_flags:
            role_attr_flags_dict = {}
            for r in role_attr_flags.split(' '):
                if r.startswith('NO'):
                    role_attr_flags_dict[r.replace('NO', '', 1)] = False
                else:
                    role_attr_flags_dict[r] = True

            for role_attr_name, role_attr_value in role_attr_flags_dict.items():
                if current_role_attrs[PRIV_TO_AUTHID_COLUMN[role_attr_name]] != role_attr_value:
                    role_attr_flags_changing = True

        if expires is not None:
            cursor.execute("SELECT %s::timestamptz;", (expires,))
            expires_with_tz = cursor.fetchone()[0]
            expires_changing = expires_with_tz != current_role_attrs.get('rolvaliduntil')
        else:
            expires_changing = False

        if not pwchanging and not role_attr_flags_changing and not expires_changing:
            return False

        alter = ['ALTER USER %(user)s' % {"user": pg_quote_identifier(user, 'role')}]
        if pwchanging:
            alter.append("WITH %(crypt)s" % {"crypt": encrypted})
            alter.append("PASSWORD %(password)s")
            alter.append(role_attr_flags)
        elif role_attr_flags:
            alter.append('WITH %s' % role_attr_flags)
        if expires is not None:
            alter.append("VALID UNTIL %(expires)s")

        query_password_data = dict(password=password, expires=expires)
        try:
            cursor.execute(' '.join(alter), query_password_data)
            changed = True
        except psycopg2.InternalError:
            e = get_exception()
            if e.pgcode == '25006':
                # Handle errors due to read-only transactions indicated by pgcode 25006
                # ERROR:  cannot execute ALTER ROLE in a read-only transaction
                changed = False
                module.fail_json(msg=e.pgerror)
                return changed
            else:
                raise psycopg2.InternalError(e)

    elif no_password_changes and role_attr_flags != '':
        # Grab role information from pg_roles instead of pg_authid
        select = "SELECT * FROM pg_roles where rolname=%(user)s"
        cursor.execute(select, {"user": user})
        # Grab current role attributes.
        current_role_attrs = cursor.fetchone()

        role_attr_flags_changing = False

        if role_attr_flags:
            role_attr_flags_dict = {}
            for r in role_attr_flags.split(' '):
                if r.startswith('NO'):
                    role_attr_flags_dict[r.replace('NO', '', 1)] = False
                else:
                    role_attr_flags_dict[r] = True

            for role_attr_name, role_attr_value in role_attr_flags_dict.items():
                if current_role_attrs[PRIV_TO_AUTHID_COLUMN[role_attr_name]] != role_attr_value:
                    role_attr_flags_changing = True

        if not role_attr_flags_changing:
            return False

        alter = ['ALTER USER %(user)s' % {"user": pg_quote_identifier(user, 'role')}]
        if role_attr_flags:
            alter.append('WITH %s' % role_attr_flags)

        try:
            cursor.execute(' '.join(alter))
        except psycopg2.InternalError:
            e = get_exception()
            if e.pgcode == '25006':
                # Handle errors due to read-only transactions indicated by pgcode 25006
                # ERROR:  cannot execute ALTER ROLE in a read-only transaction
                changed = False
                module.fail_json(msg=e.pgerror)
                return changed
            else:
                raise psycopg2.InternalError(e)

        # Grab new role attributes.
        cursor.execute(select, {"user": user})
        new_role_attrs = cursor.fetchone()

        # Detect any differences between current_ and new_role_attrs.
        changed = current_role_attrs != new_role_attrs

    return changed