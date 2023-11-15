    def commit(self, adds, changes, deletes):
        options_safe_error = options.safe_error
        def value(row, col):
            v = col.getTypedValue(row)
            if isinstance(v, TypedWrapper):
                if isinstance(v, TypedExceptionWrapper):
                    return options_safe_error
                else:
                    return None
            return v

        def values(row, cols):
            vals = []
            for c in cols:
                vals.append(value(row, c))
            return vals

        with self.conn() as conn:
            wherecols = self.keyCols or self.visibleCols
            for r in adds:
                cols = self.visibleCols
                sql = 'INSERT INTO "%s" ' % self.tableName
                sql += '("%s")' % ','.join(c.name for c in cols)
                sql += 'VALUES (%s)' % ','.join('?' for c in cols)
                self.execute(conn, sql, parms=values(r, cols))

            for r, changedcols in changes:
                sql = 'UPDATE "%s" SET ' % self.tableName
                sql += ', '.join('"%s"=?' % c.name for c in changedcols)
                self.execute(conn, sql,
                            where={c.name: c.getSavedValue(r) for c in wherecols},
                            parms=values(r, changedcols))

            for r in deletes:
                self.execute(conn, 'DELETE FROM "%s" ' % self.tableName,
                              where={c.name: c.getTypedValue(r) for c in wherecols})

            conn.commit()

        self.reload()