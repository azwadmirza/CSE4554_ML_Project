    def _fit(self, X, y, k_fold=5, k_fold_start=0, k_fold_end=None, n_repeats=1, n_repeat_start=0, compute_base_preds=True, time_limit=None, **kwargs):
        start_time = time.time()
        X = self.preprocess(X=X, preprocess=False, fit=True, compute_base_preds=compute_base_preds)
        if time_limit is not None:
            time_limit = time_limit - (time.time() - start_time)
        if len(self.models) == 0:
            type_map_raw = {column: R_FLOAT for column in self.stack_columns}
            type_group_map_special = {S_STACK: self.stack_columns}
            stacker_feature_metadata = FeatureMetadata(type_map_raw=type_map_raw, type_group_map_special=type_group_map_special)
            if self.feature_metadata is None:  # TODO: This is probably not the best way to do this
                self.feature_metadata = stacker_feature_metadata
            else:
                self.feature_metadata = self.feature_metadata.join_metadata(stacker_feature_metadata)
        super()._fit(X=X, y=y, k_fold=k_fold, k_fold_start=k_fold_start, k_fold_end=k_fold_end, n_repeats=n_repeats, n_repeat_start=n_repeat_start, time_limit=time_limit, **kwargs)