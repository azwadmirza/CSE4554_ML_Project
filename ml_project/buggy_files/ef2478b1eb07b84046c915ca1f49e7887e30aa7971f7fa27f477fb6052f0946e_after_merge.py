    def reload_sync(self, _conn=None):
        self.reset()
        with (_conn or self.conn()) as conn:
            tblname = self.tableName
            self.columns = self.getColumns(tblname, conn)
            self.recalc()
            r = self.execute(conn, 'SELECT COUNT(*) FROM "%s"' % tblname).fetchall()
            rowcount = r[0][0]
            self.rows = []
            for row in Progress(self.execute(conn, 'SELECT * FROM "%s"' % tblname), total=rowcount-1):
                self.addRow(row)