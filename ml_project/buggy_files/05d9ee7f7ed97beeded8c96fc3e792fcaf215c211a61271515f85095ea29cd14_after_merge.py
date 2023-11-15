    def _execute_and_fetch(self, session=None, **kw):
        if session is None and len(self._executed_sessions) > 0:
            session = self._executed_sessions[-1]
        try:
            # fetch first, to reduce the potential cost of submitting a graph
            return self.fetch(session=session)
        except ValueError:
            # not execute before
            return self.execute(session=session, **kw).fetch(session=session)