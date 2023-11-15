    def _fit(self, X, y, k_fold=5, k_fold_start=0, k_fold_end=None, n_repeats=1, n_repeat_start=0, compute_base_preds=True, time_limit=None, **kwargs):
        start_time = time.time()
        X = self.preprocess(X=X, preprocess=False, fit=True, compute_base_preds=compute_base_preds)
        if time_limit is not None:
            time_limit = time_limit - (time.time() - start_time)
        if len(self.models) == 0:
            if self.feature_types_metadata is None:  # TODO: This is probably not the best way to do this
                feature_types_raw = defaultdict(list)
                feature_types_raw['float'] = self.stack_columns
                feature_types_special = defaultdict(list)
                feature_types_special['stack'] = self.stack_columns
                self.feature_types_metadata = FeatureTypesMetadata(feature_types_raw=feature_types_raw, feature_types_special=feature_types_special)
            else:
                self.feature_types_metadata = copy.deepcopy(self.feature_types_metadata)
                self.feature_types_metadata.feature_types_raw['float'] += self.stack_columns
                self.feature_types_metadata.feature_types_special['stack'] += self.stack_columns
        super()._fit(X=X, y=y, k_fold=k_fold, k_fold_start=k_fold_start, k_fold_end=k_fold_end, n_repeats=n_repeats, n_repeat_start=n_repeat_start, time_limit=time_limit, **kwargs)