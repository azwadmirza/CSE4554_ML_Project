    def close(self):
        self._connection.close()
        self._connection = None