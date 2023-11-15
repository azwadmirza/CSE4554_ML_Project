    def _fit(self, X, y, k_fold=5, k_fold_start=0, k_fold_end=None, n_repeats=1, n_repeat_start=0, time_limit=None, **kwargs):
        if k_fold < 1:
            k_fold = 1
        if k_fold_end is None:
            k_fold_end = k_fold

        if self._oof_pred_proba is None and (k_fold_start != 0 or n_repeat_start != 0):
            self._load_oof()
        if n_repeat_start != self._n_repeats_finished:
            raise ValueError(f'n_repeat_start must equal self._n_repeats_finished, values: ({n_repeat_start}, {self._n_repeats_finished})')
        if n_repeats <= n_repeat_start:
            raise ValueError(f'n_repeats must be greater than n_repeat_start, values: ({n_repeats}, {n_repeat_start})')
        if k_fold_start != self._k_fold_end:
            raise ValueError(f'k_fold_start must equal previous k_fold_end, values: ({k_fold_start}, {self._k_fold_end})')
        if k_fold_start >= k_fold_end:
            # TODO: Remove this limitation if n_repeats > 1
            raise ValueError(f'k_fold_end must be greater than k_fold_start, values: ({k_fold_end}, {k_fold_start})')
        if (n_repeats - n_repeat_start) > 1 and k_fold_end != k_fold:
            # TODO: Remove this limitation
            raise ValueError(f'k_fold_end must equal k_fold when (n_repeats - n_repeat_start) > 1, values: ({k_fold_end}, {k_fold})')
        if self._k is not None and self._k != k_fold:
            raise ValueError(f'k_fold must equal previously fit k_fold value for the current n_repeat, values: (({k_fold}, {self._k})')
        fold_start = n_repeat_start * k_fold + k_fold_start
        fold_end = (n_repeats - 1) * k_fold + k_fold_end
        time_start = time.time()

        model_base = self._get_model_base()
        if self.features is not None:
            model_base.features = self.features
        model_base.feature_types_metadata = self.feature_types_metadata  # TODO: Don't pass this here

        if self.model_base is not None:
            self.save_model_base(self.model_base)
            self.model_base = None

        if k_fold == 1:
            if self._n_repeats != 0:
                raise ValueError(f'n_repeats must equal 0 when fitting a single model with k_fold < 2, values: ({self._n_repeats}, {k_fold})')
            model_base.set_contexts(path_context=self.path + model_base.name + os.path.sep)
            time_start_fit = time.time()
            model_base.fit(X_train=X, y_train=y, time_limit=time_limit, **kwargs)
            model_base.fit_time = time.time() - time_start_fit
            model_base.predict_time = None
            self._oof_pred_proba = model_base.predict_proba(X=X)  # TODO: Cheater value, will be overfit to valid set
            self._oof_pred_model_repeats = np.ones(shape=len(X), dtype=np.uint8)
            self._n_repeats = 1
            self._n_repeats_finished = 1
            self._k_per_n_repeat = [1]
            self.bagged_mode = False
            model_base.reduce_memory_size(remove_fit=True, remove_info=False, requires_save=True)
            if not self.save_bagged_folds:
                model_base.model = None
            if self.low_memory:
                self.save_child(model_base, verbose=False)
                self.models = [model_base.name]
            else:
                self.models = [model_base]
            self._add_child_times_to_bag(model=model_base)
            return

        # TODO: Preprocess data here instead of repeatedly
        kfolds = generate_kfold(X=X, y=y, n_splits=k_fold, stratified=self.is_stratified(), random_state=self._random_state, n_repeats=n_repeats)

        if self.problem_type == MULTICLASS:
            oof_pred_proba = np.zeros(shape=(len(X), len(y.unique())), dtype=np.float32)
        elif self.problem_type == SOFTCLASS:
            oof_pred_proba = np.zeros(shape=y.shape, dtype=np.float32)
        else:
            oof_pred_proba = np.zeros(shape=len(X))
        oof_pred_model_repeats = np.zeros(shape=len(X), dtype=np.uint8)

        models = []
        folds_to_fit = fold_end - fold_start
        for j in range(n_repeat_start, n_repeats):  # For each n_repeat
            cur_repeat_count = j - n_repeat_start
            fold_start_n_repeat = fold_start + cur_repeat_count * k_fold
            fold_end_n_repeat = min(fold_start_n_repeat + k_fold, fold_end)
            # TODO: Consider moving model fit inner for loop to a function to simply this code
            for i in range(fold_start_n_repeat, fold_end_n_repeat):  # For each fold
                folds_finished = i - fold_start
                folds_left = fold_end - i
                fold = kfolds[i]
                time_elapsed = time.time() - time_start
                if time_limit is not None:
                    time_left = time_limit - time_elapsed
                    required_time_per_fold = time_left / folds_left
                    time_limit_fold = required_time_per_fold * 0.8
                    if folds_finished > 0:
                        expected_time_required = time_elapsed * folds_to_fit / folds_finished
                        expected_remaining_time_required = expected_time_required * folds_left / folds_to_fit
                        if expected_remaining_time_required > time_left:
                            raise TimeLimitExceeded
                    if time_left <= 0:
                        raise TimeLimitExceeded
                else:
                    time_limit_fold = None

                time_start_fold = time.time()
                train_index, val_index = fold
                X_train, X_val = X.iloc[train_index, :], X.iloc[val_index, :]
                y_train, y_val = y.iloc[train_index], y.iloc[val_index]
                fold_model = copy.deepcopy(model_base)
                fold_model.name = f'{fold_model.name}_fold_{i}'
                fold_model.set_contexts(self.path + fold_model.name + os.path.sep)
                fold_model.fit(X_train=X_train, y_train=y_train, X_val=X_val, y_val=y_val, time_limit=time_limit_fold, **kwargs)
                time_train_end_fold = time.time()
                if time_limit is not None:  # Check to avoid unnecessarily predicting and saving a model when an Exception is going to be raised later
                    if i != (fold_end - 1):
                        time_elapsed = time.time() - time_start
                        time_left = time_limit - time_elapsed
                        expected_time_required = time_elapsed * folds_to_fit / (folds_finished + 1)
                        expected_remaining_time_required = expected_time_required * (folds_left - 1) / folds_to_fit
                        if expected_remaining_time_required > time_left:
                            raise TimeLimitExceeded
                pred_proba = fold_model.predict_proba(X_val)
                time_predict_end_fold = time.time()
                fold_model.fit_time = time_train_end_fold - time_start_fold
                fold_model.predict_time = time_predict_end_fold - time_train_end_fold
                fold_model.val_score = fold_model.score_with_y_pred_proba(y=y_val, y_pred_proba=pred_proba)
                fold_model.reduce_memory_size(remove_fit=True, remove_info=False, requires_save=True)
                if not self.save_bagged_folds:
                    fold_model.model = None
                if self.low_memory:
                    self.save_child(fold_model, verbose=False)
                    models.append(fold_model.name)
                else:
                    models.append(fold_model)
                oof_pred_proba[val_index] += pred_proba
                oof_pred_model_repeats[val_index] += 1
                self._add_child_times_to_bag(model=fold_model)
            if (fold_end_n_repeat != fold_end) or (k_fold == k_fold_end):
                self._k_per_n_repeat.append(k_fold)
        self.models += models

        self.bagged_mode = True

        if self._oof_pred_proba is None:
            self._oof_pred_proba = oof_pred_proba
            self._oof_pred_model_repeats = oof_pred_model_repeats
        else:
            self._oof_pred_proba += oof_pred_proba
            self._oof_pred_model_repeats += oof_pred_model_repeats

        self._n_repeats = n_repeats
        if k_fold == k_fold_end:
            self._k = None
            self._k_fold_end = 0
            self._n_repeats_finished = self._n_repeats
        else:
            self._k = k_fold
            self._k_fold_end = k_fold_end
            self._n_repeats_finished = self._n_repeats - 1