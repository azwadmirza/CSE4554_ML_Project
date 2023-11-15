    def manipulate_privs(self, obj_type, privs, objs, roles, target_roles,
                         state, grant_option, schema_qualifier=None, fail_on_role=True):
        """Manipulate database object privileges.

        :param obj_type: Type of database object to grant/revoke
                         privileges for.
        :param privs: Either a list of privileges to grant/revoke
                      or None if type is "group".
        :param objs: List of database objects to grant/revoke
                     privileges for.
        :param roles: Either a list of role names or "PUBLIC"
                      for the implicitly defined "PUBLIC" group
        :param target_roles: List of role names to grant/revoke
                             default privileges as.
        :param state: "present" to grant privileges, "absent" to revoke.
        :param grant_option: Only for state "present": If True, set
                             grant/admin option. If False, revoke it.
                             If None, don't change grant option.
        :param schema_qualifier: Some object types ("TABLE", "SEQUENCE",
                                 "FUNCTION") must be qualified by schema.
                                 Ignored for other Types.
        """
        # get_status: function to get current status
        if obj_type == 'table':
            get_status = partial(self.get_table_acls, schema_qualifier)
        elif obj_type == 'sequence':
            get_status = partial(self.get_sequence_acls, schema_qualifier)
        elif obj_type == 'function':
            get_status = partial(self.get_function_acls, schema_qualifier)
        elif obj_type == 'schema':
            get_status = self.get_schema_acls
        elif obj_type == 'language':
            get_status = self.get_language_acls
        elif obj_type == 'tablespace':
            get_status = self.get_tablespace_acls
        elif obj_type == 'database':
            get_status = self.get_database_acls
        elif obj_type == 'group':
            get_status = self.get_group_memberships
        elif obj_type == 'default_privs':
            get_status = partial(self.get_default_privs, schema_qualifier)
        elif obj_type == 'foreign_data_wrapper':
            get_status = self.get_foreign_data_wrapper_acls
        elif obj_type == 'foreign_server':
            get_status = self.get_foreign_server_acls
        elif obj_type == 'type':
            get_status = partial(self.get_type_acls, schema_qualifier)
        else:
            raise Error('Unsupported database object type "%s".' % obj_type)

        # Return False (nothing has changed) if there are no objs to work on.
        if not objs:
            return False

        # obj_ids: quoted db object identifiers (sometimes schema-qualified)
        if obj_type == 'function':
            obj_ids = []
            for obj in objs:
                try:
                    f, args = obj.split('(', 1)
                except Exception:
                    raise Error('Illegal function signature: "%s".' % obj)
                obj_ids.append('"%s"."%s"(%s' % (schema_qualifier, f, args))
        elif obj_type in ['table', 'sequence', 'type']:
            obj_ids = ['"%s"."%s"' % (schema_qualifier, o) for o in objs]
        else:
            obj_ids = ['"%s"' % o for o in objs]

        # set_what: SQL-fragment specifying what to set for the target roles:
        # Either group membership or privileges on objects of a certain type
        if obj_type == 'group':
            set_what = ','.join('"%s"' % i for i in obj_ids)
        elif obj_type == 'default_privs':
            # We don't want privs to be quoted here
            set_what = ','.join(privs)
        else:
            # function types are already quoted above
            if obj_type != 'function':
                obj_ids = [pg_quote_identifier(i, 'table') for i in obj_ids]
            # Note: obj_type has been checked against a set of string literals
            # and privs was escaped when it was parsed
            # Note: Underscores are replaced with spaces to support multi-word obj_type
            set_what = '%s ON %s %s' % (','.join(privs), obj_type.replace('_', ' '),
                                        ','.join(obj_ids))

        # for_whom: SQL-fragment specifying for whom to set the above
        if roles == 'PUBLIC':
            for_whom = 'PUBLIC'
        else:
            for_whom = []
            for r in roles:
                if not role_exists(self.module, self.cursor, r):
                    if fail_on_role:
                        self.module.fail_json(msg="Role '%s' does not exist" % r.strip())

                    else:
                        self.module.warn("Role '%s' does not exist, pass it" % r.strip())
                else:
                    for_whom.append('"%s"' % r)

            if not for_whom:
                return False

            for_whom = ','.join(for_whom)

        # as_who:
        as_who = None
        if target_roles:
            as_who = ','.join('"%s"' % r for r in target_roles)

        status_before = get_status(objs)

        query = QueryBuilder(state) \
            .for_objtype(obj_type) \
            .with_grant_option(grant_option) \
            .for_whom(for_whom) \
            .as_who(as_who) \
            .for_schema(schema_qualifier) \
            .set_what(set_what) \
            .for_objs(objs) \
            .build()

        executed_queries.append(query)
        self.cursor.execute(query)
        status_after = get_status(objs)
        status_before.sort()
        status_after.sort()
        return status_before != status_after