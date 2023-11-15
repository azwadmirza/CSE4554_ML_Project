        def fit(self, X, y, sample_weight=None, init_score=None, eval_set=None,
                eval_sample_weight=None, eval_init_score=None,
                session=None, run_kwargs=None, **kwargs):
            check_consistent_length(X, y, session=session, run_kwargs=run_kwargs)
            params = self.get_params(True)
            model = train(params, self._wrap_train_tuple(X, y, sample_weight, init_score),
                          eval_sets=self._wrap_eval_tuples(eval_set, eval_sample_weight, eval_init_score),
                          model_type=LGBMModelType.CLASSIFIER,
                          session=session, run_kwargs=run_kwargs, **kwargs)

            self.set_params(**model.get_params())
            self._copy_extra_params(model, self)
            return self