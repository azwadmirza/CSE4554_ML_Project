    def generate_features(self, X: DataFrame):
        if not self.fit:
            self._compute_feature_transformations()
        X_features = pd.DataFrame(index=X.index)
        for column in X.columns:
            if X[column].dtype.name == 'object':
                X[column].fillna('', inplace=True)
            else:
                X[column].fillna(np.nan, inplace=True)

        X_text_features_combined = []
        if self.feature_transformations['text_special']:
            for nlp_feature in self.feature_transformations['text_special']:
                X_text_features = self.generate_text_special(X[nlp_feature], nlp_feature)
                X_text_features_combined.append(X_text_features)
            X_text_features_combined = pd.concat(X_text_features_combined, axis=1)

        X = self.preprocess(X)

        if self.feature_transformations['raw']:
            X_features = X_features.join(X[self.feature_transformations['raw']])

        if self.feature_transformations['category']:
            X_categoricals = X[self.feature_transformations['category']]
            # TODO: Add stateful categorical generator, merge rare cases to an unknown value
            # TODO: What happens when training set has no unknown/rare values but test set does? What models can handle this?
            if 'text' in self.feature_type_family:
                self.feature_type_family_generated['text_as_category'] += self.feature_type_family['text']
            X_categoricals = X_categoricals.astype('category')
            X_features = X_features.join(X_categoricals)

        if self.feature_transformations['text_special']:
            if not self.fit:
                self.features_binned += list(X_text_features_combined.columns)
                self.feature_type_family_generated['text_special'] += list(X_text_features_combined.columns)
            X_features = X_features.join(X_text_features_combined)

        if self.feature_transformations['datetime']:
            for datetime_feature in self.feature_transformations['datetime']:
                X_features[datetime_feature] = pd.to_datetime(X[datetime_feature])
                X_features[datetime_feature] = pd.to_numeric(X_features[datetime_feature])  # TODO: Use actual date info
                self.feature_type_family_generated['datetime'].append(datetime_feature)
                # TODO: Add fastai date features

        if self.feature_transformations['text_ngram']:
            # Combine Text Fields
            features_nlp_current = ['__nlp__']

            if not self.fit:
                features_nlp_to_remove = []
                logger.log(15, 'Fitting vectorizer for text features: ' + str(self.feature_transformations['text_ngram']))
                for nlp_feature in features_nlp_current:
                    # TODO: Preprocess text?
                    if nlp_feature == '__nlp__':
                        text_list = list(set(['. '.join(row) for row in X[self.feature_transformations['text_ngram']].values]))
                    else:
                        text_list = list(X[nlp_feature].drop_duplicates().values)
                    vectorizer_raw = copy.deepcopy(self.vectorizer_default_raw)
                    try:
                        vectorizer_fit, _ = self.train_vectorizer(text_list, vectorizer_raw)
                        self.vectorizers.append(vectorizer_fit)
                    except ValueError:
                        logger.debug("Removing 'text_ngram' features due to error")
                        features_nlp_to_remove = self.feature_transformations['text_ngram']

                self.feature_transformations['text_ngram'] = [feature for feature in self.feature_transformations['text_ngram'] if feature not in features_nlp_to_remove]

            X_features_cols_prior_to_nlp = list(X_features.columns)
            downsample_ratio = None
            nlp_failure_count = 0
            keep_trying_nlp = True
            while keep_trying_nlp:
                try:
                    X_nlp_features_combined = self.generate_text_ngrams(X=X, features_nlp_current=features_nlp_current, downsample_ratio=downsample_ratio)

                    if self.feature_transformations['text_ngram']:
                        X_features = X_features.join(X_nlp_features_combined)

                    if not self.fit:
                        self.feature_type_family_generated['text_ngram'] += list(X_nlp_features_combined.columns)
                    keep_trying_nlp = False
                except Exception as err:
                    nlp_failure_count += 1
                    if self.fit:
                        logger.exception('Error: OOM error during NLP feature transform, unrecoverable. Increase memory allocation or reduce data size to avoid this error.')
                        raise
                    traceback.print_tb(err.__traceback__)

                    X_features = X_features[X_features_cols_prior_to_nlp]
                    skip_nlp = False
                    for vectorizer in self.vectorizers:
                        vocab_size = len(vectorizer.vocabulary_)
                        if vocab_size <= 50:
                            skip_nlp = True
                            break
                    else:
                        if nlp_failure_count >= 3:
                            skip_nlp = True

                    if skip_nlp:
                        logger.log(15, 'Warning: ngrams generation resulted in OOM error, removing ngrams features. If you want to use ngrams for this problem, increase memory allocation for AutoGluon.')
                        logger.debug(str(err))
                        self.vectorizers = []
                        if 'text_ngram' in self.feature_transformations:
                            self.feature_transformations.pop('text_ngram')
                        if 'text_ngram' in self.feature_type_family_generated:
                            self.feature_type_family_generated.pop('text_ngram')
                        self.enable_nlp_features = False
                        keep_trying_nlp = False
                    else:
                        logger.log(15, 'Warning: ngrams generation resulted in OOM error, attempting to reduce ngram feature count. If you want to optimally use ngrams for this problem, increase memory allocation for AutoGluon.')
                        logger.debug(str(err))
                        downsample_ratio = 0.25

        return X_features