    def _fit(self, X: DataFrame, X_val: DataFrame = None, scheduler_options=None, hyperparameter_tune=False,
            feature_prune=False, holdout_frac=0.1, num_bagging_folds=0, num_bagging_sets=1, stack_ensemble_levels=0,
            hyperparameters=None, ag_args_fit=None, excluded_model_types=None, time_limit=None, save_data=False, save_bagged_folds=True, verbosity=2):
        """ Arguments:
                X (DataFrame): training data
                X_val (DataFrame): data used for hyperparameter tuning. Note: final model may be trained using this data as well as training data
                hyperparameter_tune (bool): whether to tune hyperparameters or simply use default values
                feature_prune (bool): whether to perform feature selection
                scheduler_options (tuple: (search_strategy, dict): Options for scheduler
                holdout_frac (float): Fraction of data to hold out for evaluating validation performance (ignored if X_val != None, ignored if kfolds != 0)
                num_bagging_folds (int): kfolds used for bagging of models, roughly increases model training time by a factor of k (0: disabled)
                num_bagging_sets (int): number of repeats of kfold bagging to perform (values must be >= 1),
                    total number of models trained during bagging = num_bagging_folds * num_bagging_sets
                stack_ensemble_levels : (int) Number of stacking levels to use in ensemble stacking. Roughly increases model training time by factor of stack_levels+1 (0: disabled)
                    Default is 0 (disabled). Use values between 1-3 to improve model quality.
                    Ignored unless kfolds is also set >= 2
                hyperparameters (dict): keys = hyperparameters + search-spaces for each type of model we should train.
        """
        if hyperparameters is None:
            hyperparameters = {'NN': {}, 'GBM': {}}
        # TODO: if provided, feature_types in X, X_val are ignored right now, need to pass to Learner/trainer and update this documentation.
        if time_limit:
            self.time_limit = time_limit
            logger.log(20, f'Beginning AutoGluon training ... Time limit = {time_limit}s')
        else:
            self.time_limit = 1e7
            logger.log(20, 'Beginning AutoGluon training ...')
        logger.log(20, f'AutoGluon will save models to {self.path}')
        logger.log(20, f'AutoGluon Version:  {self.version}')
        logger.log(20, f'Train Data Rows:    {len(X)}')
        logger.log(20, f'Train Data Columns: {len(X.columns)}')
        if X_val is not None:
            logger.log(20, f'Tuning Data Rows:    {len(X_val)}')
            logger.log(20, f'Tuning Data Columns: {len(X_val.columns)}')
        time_preprocessing_start = time.time()
        logger.log(20, 'Preprocessing data ...')
        X, y, X_val, y_val, holdout_frac, num_bagging_folds = self.general_data_processing(X, X_val, holdout_frac, num_bagging_folds)
        time_preprocessing_end = time.time()
        self.time_fit_preprocessing = time_preprocessing_end - time_preprocessing_start
        logger.log(20, f'\tData preprocessing and feature engineering runtime = {round(self.time_fit_preprocessing, 2)}s ...')
        if time_limit:
            time_limit_trainer = time_limit - self.time_fit_preprocessing
        else:
            time_limit_trainer = None

        trainer = self.trainer_type(
            path=self.model_context,
            problem_type=self.label_cleaner.problem_type_transform,
            eval_metric=self.eval_metric,
            stopping_metric=self.stopping_metric,
            num_classes=self.label_cleaner.num_classes,
            feature_types_metadata=self.feature_generator.feature_types_metadata,
            low_memory=True,
            kfolds=num_bagging_folds,
            n_repeats=num_bagging_sets,
            stack_ensemble_levels=stack_ensemble_levels,
            scheduler_options=scheduler_options,
            time_limit=time_limit_trainer,
            save_data=save_data,
            save_bagged_folds=save_bagged_folds,
            random_seed=self.random_seed,
            verbosity=verbosity
        )

        self.trainer_path = trainer.path
        if self.eval_metric is None:
            self.eval_metric = trainer.eval_metric
        if self.stopping_metric is None:
            self.stopping_metric = trainer.stopping_metric

        self.save()
        trainer.train(X, y, X_val, y_val, hyperparameter_tune=hyperparameter_tune, feature_prune=feature_prune, holdout_frac=holdout_frac,
                      hyperparameters=hyperparameters, ag_args_fit=ag_args_fit, excluded_model_types=excluded_model_types)
        self.save_trainer(trainer=trainer)
        time_end = time.time()
        self.time_fit_training = time_end - time_preprocessing_end
        self.time_fit_total = time_end - time_preprocessing_start
        logger.log(20, f'AutoGluon training complete, total runtime = {round(self.time_fit_total, 2)}s ...')