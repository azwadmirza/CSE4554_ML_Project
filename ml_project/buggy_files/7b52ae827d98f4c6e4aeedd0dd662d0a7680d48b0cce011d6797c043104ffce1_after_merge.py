    def fetchone(self, result, dbapi_cursor, hard_close=False):
        if not self._rowbuffer:
            self._buffer_rows(result, dbapi_cursor)
            if not self._rowbuffer:
                try:
                    result._soft_close(hard=hard_close)
                except BaseException as e:
                    self.handle_exception(result, dbapi_cursor, e)
                return None
        return self._rowbuffer.popleft()