        def predict(self, data, **kw):
            session = kw.pop('session', None)
            run_kwargs = kw.pop('run_kwargs', dict())
            run = kw.pop('run', True)
            if kw:
                raise TypeError("predict got an unexpected "
                                f"keyword argument '{next(iter(kw))}'")
            prob = predict(self.get_booster(), data, run=False)
            if prob.ndim > 1:
                prediction = mt.argmax(prob, axis=1)
            else:
                prediction = (prob > 0.5).astype(mt.int64)
            if run:
                prediction.execute(session=session, **run_kwargs)
            return prediction