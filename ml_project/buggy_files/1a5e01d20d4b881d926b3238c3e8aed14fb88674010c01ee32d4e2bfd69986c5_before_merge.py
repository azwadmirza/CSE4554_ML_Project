    def fit(
        self,
        X,  # type: TwoDimArrayLikeType
        y=None,  # type: Optional[Union[OneDimArrayLikeType, TwoDimArrayLikeType]]
        groups=None,  # type: Optional[OneDimArrayLikeType]
        **fit_params  # type: Any
    ):
        # type: (...) -> 'OptunaSearchCV'
        """Run fit with all sets of parameters.

        Args:
            X:
                Training data.

            y:
                Target variable.

            groups:
                Group labels for the samples used while splitting the dataset
                into train/test set.

            **fit_params:
                Parameters passed to ``fit`` on the estimator.

        Returns:
            self:
                Return self.
        """

        self._check_params()

        random_state = check_random_state(self.random_state)
        max_samples = self.subsample
        n_samples = _num_samples(X)
        old_level = _logger.getEffectiveLevel()

        if self.verbose > 1:
            _logger.setLevel(DEBUG)
        elif self.verbose > 0:
            _logger.setLevel(INFO)
        else:
            _logger.setLevel(WARNING)

        self.sample_indices_ = np.arange(n_samples)

        if type(max_samples) is float:
            max_samples = int(max_samples * n_samples)

        if max_samples < n_samples:
            self.sample_indices_ = random_state.choice(
                self.sample_indices_,
                max_samples,
                replace=False
            )

            self.sample_indices_.sort()

        X_res = _safe_indexing(X, self.sample_indices_)
        y_res = _safe_indexing(y, self.sample_indices_)
        groups_res = _safe_indexing(groups, self.sample_indices_)
        fit_params_res = fit_params

        if fit_params_res is not None:
            fit_params_res = {
                key: _index_param_value(
                    X,
                    value,
                    self.sample_indices_
                ) for key, value in fit_params.items()
            }

        classifier = is_classifier(self.estimator)
        cv = check_cv(self.cv, y_res, classifier)

        self.n_splits_ = cv.get_n_splits(X_res, y_res, groups=groups_res)
        self.scorer_ = check_scoring(self.estimator, scoring=self.scoring)

        if self.study is None:
            seed = random_state.randint(0, np.iinfo('int32').max)
            sampler = samplers.TPESampler(seed=seed)

            self.study_ = study_module.create_study(
                direction='maximize',
                sampler=sampler
            )

        else:
            self.study_ = self.study

        objective = _Objective(
            self.estimator,
            self.param_distributions,
            X_res,
            y_res,
            cv,
            self.enable_pruning,
            self.error_score,
            fit_params_res,
            groups_res,
            self.max_iter,
            self.return_train_score,
            self.scorer_
        )

        _logger.info(
            'Searching the best hyperparameters using {} '
            'samples...'.format(_num_samples(self.sample_indices_))
        )

        self.study_.optimize(
            objective,
            n_jobs=self.n_jobs,
            n_trials=self.n_trials,
            timeout=self.timeout
        )

        _logger.info('Finished hyperparemeter search!')

        if self.refit:
            self._refit(X, y, **fit_params)

        _logger.setLevel(old_level)

        return self