    def exc_info(self):
        """
        Holds the exc_info three-tuple raised by the function if the
        greenlet finished with an error. Otherwise a false value.

        .. note:: This is a provisional API and may change.

        .. versionadded:: 1.1
        """
        ei = self._exc_info
        if ei is not None and ei[0] is not None:
            return (ei[0], ei[1], load_traceback(ei[2]))