    def general_data_processing(self, X: DataFrame, X_val: DataFrame, holdout_frac: float, num_bagging_folds: int):
        """ General data processing steps used for all models. """
        X = copy.deepcopy(X)
        # TODO: We should probably uncomment the below lines, NaN label should be treated as just another value in multiclass classification -> We will have to remove missing, compute problem type, and add back missing if multiclass
        # if self.problem_type == MULTICLASS:
        #     X[self.label] = X[self.label].fillna('')

        # Remove all examples with missing labels from this dataset:
        missinglabel_inds = [index for index, x in X[self.label].isna().iteritems() if x]
        if len(missinglabel_inds) > 0:
            logger.warning(f"Warning: Ignoring {len(missinglabel_inds)} (out of {len(X)}) training examples for which the label value in column '{self.label}' is missing")
            X = X.drop(missinglabel_inds, axis=0)

        if self.problem_type is None:
            self.problem_type = self.infer_problem_type(X[self.label])

        if X_val is not None and self.label in X_val.columns:
            # TODO: This is not an ideal solution, instead check if bagging and X_val exists with label, then merge them prior to entering general data processing.
            #  This solution should handle virtually all cases correctly, only downside is it might cut more classes than it needs to.
            self.threshold, holdout_frac, num_bagging_folds = self.adjust_threshold_if_necessary(X[self.label], threshold=self.threshold, holdout_frac=1, num_bagging_folds=num_bagging_folds)
        else:
            self.threshold, holdout_frac, num_bagging_folds = self.adjust_threshold_if_necessary(X[self.label], threshold=self.threshold, holdout_frac=holdout_frac, num_bagging_folds=num_bagging_folds)

        if (self.eval_metric is not None) and (self.eval_metric.name in ['log_loss', 'pac_score']) and (self.problem_type == MULTICLASS):
            X = augment_rare_classes(X, self.label, self.threshold)

        # Gets labels prior to removal of infrequent classes
        y_uncleaned = X[self.label].copy()

        self.cleaner = Cleaner.construct(problem_type=self.problem_type, label=self.label, threshold=self.threshold)
        # TODO: What if all classes in X are low frequency in multiclass? Currently we would crash. Not certain how many problems actually have this property
        X = self.cleaner.fit_transform(X)  # TODO: Consider merging cleaner into label_cleaner
        X, y = self.extract_label(X)
        self.label_cleaner = LabelCleaner.construct(problem_type=self.problem_type, y=y, y_uncleaned=y_uncleaned)
        y = self.label_cleaner.transform(y)

        if self.label_cleaner.num_classes is not None:
            logger.log(20, f'Train Data Class Count: {self.label_cleaner.num_classes}')

        if X_val is not None and self.label in X_val.columns:
            X_val = self.cleaner.transform(X_val)
            if len(X_val) == 0:
                logger.warning('All X_val data contained low frequency classes, ignoring X_val and generating from subset of X')
                X_val = None
                y_val = None
            else:
                X_val, y_val = self.extract_label(X_val)
                y_val = self.label_cleaner.transform(y_val)
        else:
            y_val = None

        # TODO: Move this up to top of data before removing data, this way our feature generator is better
        if X_val is not None:
            # Do this if working with SKLearn models, otherwise categorical features may perform very badly on the test set
            logger.log(15, 'Performing general data preprocessing with merged train & validation data, so validation performance may not accurately reflect performance on new test data')
            X_super = pd.concat([X, X_val], ignore_index=True)
            X_super = self.feature_generator.fit_transform(X_super, banned_features=self.submission_columns, drop_duplicates=False)
            X = X_super.head(len(X)).set_index(X.index)
            X_val = X_super.tail(len(X_val)).set_index(X_val.index)
            del X_super
        else:
            X = self.feature_generator.fit_transform(X, banned_features=self.submission_columns, drop_duplicates=False)

        return X, y, X_val, y_val, holdout_frac, num_bagging_folds