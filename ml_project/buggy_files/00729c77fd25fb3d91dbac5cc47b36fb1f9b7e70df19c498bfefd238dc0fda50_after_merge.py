    def _get_selectable(self, engine_or_conn, columns=None):
        import sqlalchemy as sa
        from sqlalchemy import sql
        from sqlalchemy.exc import NoSuchTableError

        # process table_name
        if self._selectable is not None:
            selectable = self._selectable
        else:
            if isinstance(self._table_or_sql, sa.Table):
                selectable = self._table_or_sql
                self._table_or_sql = selectable.name
            else:
                m = sa.MetaData()
                try:
                    selectable = sa.Table(self._table_or_sql, m, autoload=True,
                                          autoload_with=engine_or_conn, schema=self._schema)
                except NoSuchTableError:
                    temp_name_1 = 't1_' + binascii.b2a_hex(uuid.uuid4().bytes).decode()
                    temp_name_2 = 't2_' + binascii.b2a_hex(uuid.uuid4().bytes).decode()
                    if columns:
                        selectable = sql.text(self._table_or_sql).columns(*[sql.column(c) for c in columns]) \
                            .alias(temp_name_2)
                    else:
                        selectable = sql.select(
                            '*', from_obj=sql.text('(%s) AS %s' % (self._table_or_sql, temp_name_1))) \
                            .alias(temp_name_2)
                    self._selectable = selectable
        return selectable