        def predict(self, data, **kw):
            session = kw.pop('session', None)
            run_kwargs = kw.pop('run_kwargs', None)
            if kw:
                raise TypeError("predict got an unexpected "
                                f"keyword argument '{next(iter(kw))}'")
            return predict(self.get_booster(), data,
                           session=session, run_kwargs=run_kwargs)