    def fetchmany(self, result, dbapi_cursor, size=None):
        if size is None:
            return self.fetchall(result, dbapi_cursor)

        buf = list(self._rowbuffer)
        lb = len(buf)
        if size > lb:
            try:
                buf.extend(dbapi_cursor.fetchmany(size - lb))
            except BaseException as e:
                self.handle_exception(result, e)

        result = buf[0:size]
        self._rowbuffer = collections.deque(buf[size:])
        return result