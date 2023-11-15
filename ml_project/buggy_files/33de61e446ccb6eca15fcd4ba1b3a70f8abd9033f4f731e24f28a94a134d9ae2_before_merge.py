    def preprocess(self, X):
        if self.features is not None:
            # TODO: In online-inference this becomes expensive, add option to remove it (only safe in controlled environment where it is already known features are present
            if list(X.columns) != self.features:
                return X[self.features]
        else:
            self.features = list(X.columns)  # TODO: add fit and transform versions of preprocess instead of doing this
            ignored_feature_types_raw = self.params_aux.get('ignored_feature_types_raw', [])
            if ignored_feature_types_raw:
                for ignored_feature_type in ignored_feature_types_raw:
                    self.features = [feature for feature in self.features if feature not in self.feature_types_metadata.feature_types_raw[ignored_feature_type]]
            ignored_feature_types_special = self.params_aux.get('ignored_feature_types_special', [])
            if ignored_feature_types_special:
                for ignored_feature_type in ignored_feature_types_special:
                    self.features = [feature for feature in self.features if feature not in self.feature_types_metadata.feature_types_special[ignored_feature_type]]
            if not self.features:
                raise NoValidFeatures
            if ignored_feature_types_raw or ignored_feature_types_special:
                if list(X.columns) != self.features:
                    X = X[self.features]
        return X