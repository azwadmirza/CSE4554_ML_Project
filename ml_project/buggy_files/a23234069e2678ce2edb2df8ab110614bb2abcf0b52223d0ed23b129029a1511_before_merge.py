    def __del__(self):
        if GL:  # because of pytest fail otherwise
            GL.glDeleteLists(self._listID, 1)