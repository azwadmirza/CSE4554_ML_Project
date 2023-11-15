    def get_columns(self, connection, tablename, dbname, owner, schema, **kw):
        # Get base columns
        columns = ischema.columns
        computed_cols = ischema.computed_columns
        if owner:
            whereclause = sql.and_(
                columns.c.table_name == tablename,
                columns.c.table_schema == owner,
            )
            table_fullname = "%s.%s" % (owner, tablename)
            full_name = columns.c.table_schema + "." + columns.c.table_name
            join_on = computed_cols.c.object_id == func.object_id(full_name)
        else:
            whereclause = columns.c.table_name == tablename
            table_fullname = tablename
            join_on = computed_cols.c.object_id == func.object_id(
                columns.c.table_name
            )

        join_on = sql.and_(
            join_on, columns.c.column_name == computed_cols.c.name
        )
        join = columns.join(computed_cols, onclause=join_on, isouter=True)

        if self._supports_nvarchar_max:
            computed_definition = computed_cols.c.definition
        else:
            # tds_version 4.2 does not support NVARCHAR(MAX)
            computed_definition = sql.cast(
                computed_cols.c.definition, NVARCHAR(4000)
            )

        s = sql.select(
            [columns, computed_definition, computed_cols.c.is_persisted],
            whereclause,
            from_obj=join,
            order_by=[columns.c.ordinal_position],
        )

        c = connection.execute(s)
        cols = []

        while True:
            row = c.fetchone()
            if row is None:
                break
            name = row[columns.c.column_name]
            type_ = row[columns.c.data_type]
            nullable = row[columns.c.is_nullable] == "YES"
            charlen = row[columns.c.character_maximum_length]
            numericprec = row[columns.c.numeric_precision]
            numericscale = row[columns.c.numeric_scale]
            default = row[columns.c.column_default]
            collation = row[columns.c.collation_name]
            definition = row[computed_definition]
            is_persisted = row[computed_cols.c.is_persisted]

            coltype = self.ischema_names.get(type_, None)

            kwargs = {}
            if coltype in (
                MSString,
                MSChar,
                MSNVarchar,
                MSNChar,
                MSText,
                MSNText,
                MSBinary,
                MSVarBinary,
                sqltypes.LargeBinary,
            ):
                if charlen == -1:
                    charlen = None
                kwargs["length"] = charlen
                if collation:
                    kwargs["collation"] = collation

            if coltype is None:
                util.warn(
                    "Did not recognize type '%s' of column '%s'"
                    % (type_, name)
                )
                coltype = sqltypes.NULLTYPE
            else:
                if issubclass(coltype, sqltypes.Numeric):
                    kwargs["precision"] = numericprec

                    if not issubclass(coltype, sqltypes.Float):
                        kwargs["scale"] = numericscale

                coltype = coltype(**kwargs)
            cdict = {
                "name": name,
                "type": coltype,
                "nullable": nullable,
                "default": default,
                "autoincrement": False,
            }

            if definition is not None and is_persisted is not None:
                cdict["computed"] = {
                    "sqltext": definition,
                    "persisted": is_persisted,
                }

            cols.append(cdict)
        # autoincrement and identity
        colmap = {}
        for col in cols:
            colmap[col["name"]] = col
        # We also run an sp_columns to check for identity columns:
        cursor = connection.execute(
            sql.text(
                "EXEC sp_columns @table_name = :table_name, "
                "@table_owner = :table_owner",
            ),
            {"table_name": tablename, "table_owner": owner},
        )
        ic = None
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            (col_name, type_name) = row[3], row[5]
            if type_name.endswith("identity") and col_name in colmap:
                ic = col_name
                colmap[col_name]["autoincrement"] = True
                colmap[col_name]["dialect_options"] = {
                    "mssql_identity_start": 1,
                    "mssql_identity_increment": 1,
                }
                break
        cursor.close()

        if ic is not None and self.server_version_info >= MS_2005_VERSION:
            table_fullname = "%s.%s" % (owner, tablename)
            cursor = connection.execute(
                "select ident_seed('%s'), ident_incr('%s')"
                % (table_fullname, table_fullname)
            )

            row = cursor.first()
            if row is not None and row[0] is not None:
                colmap[ic]["dialect_options"].update(
                    {
                        "mssql_identity_start": int(row[0]),
                        "mssql_identity_increment": int(row[1]),
                    }
                )
        return cols