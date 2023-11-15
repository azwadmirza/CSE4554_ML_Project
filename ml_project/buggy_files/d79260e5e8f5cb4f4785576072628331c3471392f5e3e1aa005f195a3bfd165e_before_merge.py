    def execute(self, session=None, n_parallel=None):
        from ..session import Session

        if session is None:
            session = Session.default_or_local()
        return session.run(*self, n_parallel=n_parallel)