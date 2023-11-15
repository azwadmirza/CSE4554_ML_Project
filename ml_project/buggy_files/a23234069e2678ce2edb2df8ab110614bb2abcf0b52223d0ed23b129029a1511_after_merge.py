    def __del__(self):
        if GL:  # because of pytest fail otherwise
            try:
                GL.glDeleteLists(self._listID, 1)
            except ModuleNotFoundError:
                pass  # if pyglet no longer exists