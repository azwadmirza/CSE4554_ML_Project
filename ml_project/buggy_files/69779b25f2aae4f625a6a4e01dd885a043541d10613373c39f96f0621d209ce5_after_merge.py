def user_add(cursor, user, password, role_attr_flags, encrypted, expires):
    """Create a new database user (role)."""
    # Note: role_attr_flags escaped by parse_role_attrs and encrypted is a
    # literal
    query_password_data = dict(password=password, expires=expires)
    query = ['CREATE USER %(user)s' %
             {"user": pg_quote_identifier(user, 'role')}]
    if password is not None:
        query.append("WITH %(crypt)s" % {"crypt": encrypted})
        query.append("PASSWORD %(password)s")
    if expires is not None:
        query.append("VALID UNTIL %(expires)s")
    query.append(role_attr_flags)
    query = ' '.join(query)
    cursor.execute(query, query_password_data)
    return True