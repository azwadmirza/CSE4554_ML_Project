    def train_single_full(self, X_train, y_train, X_val, y_val, model: AbstractModel, feature_prune=False,
                          hyperparameter_tune=True, stack_name='core', kfolds=None, k_fold_start=0, k_fold_end=None, n_repeats=None, n_repeat_start=0, level=0, time_limit=None):
        if (n_repeat_start == 0) and (k_fold_start == 0):
            model.feature_types_metadata = copy.deepcopy(self.feature_types_metadata)  # TODO: Don't set feature_types_metadata here
        if feature_prune:
            if n_repeat_start != 0:
                raise ValueError('n_repeat_start must be 0 to feature_prune, value = ' + str(n_repeat_start))
            elif k_fold_start != 0:
                raise ValueError('k_fold_start must be 0 to feature_prune, value = ' + str(k_fold_start))
            self.autotune(X_train=X_train, X_holdout=X_val, y_train=y_train, y_holdout=y_val, model_base=model)  # TODO: Update to use CV instead of holdout
        if hyperparameter_tune:
            if self.scheduler_func is None or self.scheduler_options is None:
                raise ValueError("scheduler_options cannot be None when hyperparameter_tune = True")
            if n_repeat_start != 0:
                raise ValueError('n_repeat_start must be 0 to hyperparameter_tune, value = ' + str(n_repeat_start))
            elif k_fold_start != 0:
                raise ValueError('k_fold_start must be 0 to hyperparameter_tune, value = ' + str(k_fold_start))
            # hpo_models (dict): keys = model_names, values = model_paths
            try:
                if isinstance(model, BaggedEnsembleModel):
                    hpo_models, hpo_model_performances, hpo_results = model.hyperparameter_tune(X=X_train, y=y_train, k_fold=kfolds, scheduler_options=(self.scheduler_func, self.scheduler_options), verbosity=self.verbosity)
                else:
                    hpo_models, hpo_model_performances, hpo_results = model.hyperparameter_tune(X_train=X_train, y_train=y_train, X_val=X_val, y_val=y_val, scheduler_options=(self.scheduler_func, self.scheduler_options), verbosity=self.verbosity)
            except Exception as err:
                if self.verbosity >= 1:
                    traceback.print_tb(err.__traceback__)
                logger.exception('Warning: Exception caused ' + model.name + ' to fail during hyperparameter tuning... Skipping this model.')
                logger.debug(err)
                del model
                model_names_trained = []
            else:
                self.hpo_results[model.name] = hpo_results
                model_names_trained = []
                for model_hpo_name, model_path in hpo_models.items():
                    model_hpo = self.load_model(model_hpo_name, path=model_path, model_type=type(model))
                    self.add_model(model=model_hpo, stack_name=stack_name, level=level)
                    model_names_trained.append(model_hpo.name)
        else:
            model_names_trained = self.train_and_save(X_train, y_train, X_val, y_val, model, stack_name=stack_name, kfolds=kfolds, k_fold_start=k_fold_start, k_fold_end=k_fold_end, n_repeats=n_repeats, n_repeat_start=n_repeat_start, level=level, time_limit=time_limit)
        self.save()
        return model_names_trained