    def exec_once(self, *args, **kw):
        """Execute this event, but only if it has not been
        executed already for this collection."""

        if not self._exec_once:
            with self._exec_once_mutex:
                if not self._exec_once:
                    try:
                        self(*args, **kw)
                    finally:
                        self._exec_once = True