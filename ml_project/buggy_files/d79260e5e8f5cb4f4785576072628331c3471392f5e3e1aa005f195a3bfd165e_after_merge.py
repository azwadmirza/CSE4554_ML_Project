    def execute(self, session=None, **kw):
        from ..session import Session

        if session is None:
            session = Session.default_or_local()
        return session.run(*self, **kw)