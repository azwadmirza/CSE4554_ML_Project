    def execute(self, conn, sql, where={}, parms=None):
        parms = parms or []
        if where:
            sql += ' WHERE %s' % " AND ".join("%s=?" % k for k in where)
        status(sql)
        parms += list(where.values())
        return conn.execute(sql, parms)