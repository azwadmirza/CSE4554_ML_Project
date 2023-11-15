    def preprocess(self, X):
        if self.features is not None:
            # TODO: In online-inference this becomes expensive, add option to remove it (only safe in controlled environment where it is already known features are present
            if list(X.columns) != self.features:
                return X[self.features]
        else:
            self.features = list(X.columns)  # TODO: add fit and transform versions of preprocess instead of doing this
            ignored_type_group_raw = self.params_aux.get('ignored_type_group_raw', [])
            ignored_type_group_special = self.params_aux.get('ignored_type_group_special', [])
            valid_features = self.feature_metadata.get_features(invalid_raw_types=ignored_type_group_raw, invalid_special_types=ignored_type_group_special)
            self.features = [feature for feature in self.features if feature in valid_features]
            if not self.features:
                raise NoValidFeatures
            if list(X.columns) != self.features:
                X = X[self.features]
        return X