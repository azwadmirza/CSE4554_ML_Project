    def hyperparameter_tune(self, X, y, k_fold, scheduler_options=None, compute_base_preds=True, **kwargs):
        if len(self.models) != 0:
            raise ValueError('self.models must be empty to call hyperparameter_tune, value: %s' % self.models)

        if len(self.models) == 0:
            type_map_raw = {column: R_FLOAT for column in self.stack_columns}
            type_group_map_special = {S_STACK: self.stack_columns}
            stacker_feature_metadata = FeatureMetadata(type_map_raw=type_map_raw, type_group_map_special=type_group_map_special)
            if self.feature_metadata is None:  # TODO: This is probably not the best way to do this
                self.feature_metadata = stacker_feature_metadata
            else:
                self.feature_metadata = self.feature_metadata.join_metadata(stacker_feature_metadata)
        self.model_base.feature_metadata = self.feature_metadata  # TODO: Move this

        # TODO: Preprocess data here instead of repeatedly
        X = self.preprocess(X=X, preprocess=False, fit=True, compute_base_preds=compute_base_preds)
        kfolds = generate_kfold(X=X, y=y, n_splits=k_fold, stratified=self.is_stratified(), random_state=self._random_state, n_repeats=1)

        train_index, test_index = kfolds[0]
        X_train, X_val = X.iloc[train_index, :], X.iloc[test_index, :]
        y_train, y_val = y.iloc[train_index], y.iloc[test_index]
        orig_time = scheduler_options[1]['time_out']
        scheduler_options[1]['time_out'] = orig_time * 0.8  # TODO: Scheduler doesn't early stop on final model, this is a safety net. Scheduler should be updated to early stop
        hpo_models, hpo_model_performances, hpo_results = self.model_base.hyperparameter_tune(X_train=X_train, y_train=y_train, X_val=X_val, y_val=y_val, scheduler_options=scheduler_options, **kwargs)
        scheduler_options[1]['time_out'] = orig_time

        stackers = {}
        stackers_performance = {}
        for i, (model_name, model_path) in enumerate(hpo_models.items()):
            child: AbstractModel = self._child_type.load(path=model_path)
            y_pred_proba = child.predict_proba(X_val)

            # TODO: Create new StackerEnsemble Here
            stacker = copy.deepcopy(self)
            stacker.name = stacker.name + os.path.sep + str(i)
            stacker.set_contexts(self.path_root + stacker.name + os.path.sep)

            if self.problem_type == MULTICLASS:
                oof_pred_proba = np.zeros(shape=(len(X), len(y.unique())))
            else:
                oof_pred_proba = np.zeros(shape=len(X))
            oof_pred_model_repeats = np.zeros(shape=len(X))
            oof_pred_proba[test_index] += y_pred_proba
            oof_pred_model_repeats[test_index] += 1

            stacker.model_base = None
            child.set_contexts(stacker.path + child.name + os.path.sep)
            stacker.save_model_base(child.convert_to_template())

            stacker._k = k_fold
            stacker._k_fold_end = 1
            stacker._n_repeats = 1
            stacker._oof_pred_proba = oof_pred_proba
            stacker._oof_pred_model_repeats = oof_pred_model_repeats
            child.name = child.name + '_fold_0'
            child.set_contexts(stacker.path + child.name + os.path.sep)
            if not self.save_bagged_folds:
                child.model = None
            if stacker.low_memory:
                stacker.save_child(child, verbose=False)
                stacker.models.append(child.name)
            else:
                stacker.models.append(child)
            stacker.val_score = child.val_score
            stacker._add_child_times_to_bag(model=child)

            stacker.save()
            stackers[stacker.name] = stacker.path
            stackers_performance[stacker.name] = stacker.val_score

        # TODO: hpo_results likely not correct because no renames
        return stackers, stackers_performance, hpo_results