    def getColumns(self, tableName, conn):
        cols = []
        for i, r in enumerate(self.execute(conn, 'PRAGMA TABLE_INFO("%s")' % tableName)):
            c = DeferredSetColumn(r[1],
                    getter=lambda col,row,idx=i: row[idx],
                    setter=lambda col,row,val: col.sheet.commit())
            t = r[2].lower()
            if t == 'integer':
                c.type = int
            elif t == 'text':
                c.type = anytype
            elif t == 'blob':
                c.type = str
            elif t == 'real':
                c.type = float
            else:
                status('unknown sqlite type "%s"' % t)

            cols.append(c)
            if r[-1]:
                self.setKeys([c])

        return cols