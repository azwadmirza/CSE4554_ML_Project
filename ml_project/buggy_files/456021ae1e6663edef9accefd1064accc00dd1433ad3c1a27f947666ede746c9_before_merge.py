        def predict(self, X, **kw):
            session = kw.pop('session', None)
            run_kwargs = kw.pop('run_kwargs', None)
            return predict(self, X, session=session, run_kwargs=run_kwargs, **kw)