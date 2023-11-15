        def predict(self, data, **kw):
            session = kw.pop('session', None)
            run_kwargs = kw.pop('run_kwargs', None)
            return predict(self.get_booster(), data,
                           session=session, run_kwargs=run_kwargs, **kw)