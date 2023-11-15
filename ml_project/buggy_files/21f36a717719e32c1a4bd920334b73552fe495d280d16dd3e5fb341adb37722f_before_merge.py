    def _validate_input(self, X, y, incremental):
        X, y = check_X_y(X, y, accept_sparse=['csr', 'csc', 'coo'],
                         multi_output=True)
        if y.ndim == 2 and y.shape[1] == 1:
            y = column_or_1d(y, warn=True)
        self.label_binarizer_.fit(y)

        if not hasattr(self, 'classes_') or not incremental:
            self.classes_ = self.label_binarizer_.classes_
        else:
            classes = self.label_binarizer_.classes_
            if not np.all(np.in1d(classes, self.classes_)):
                raise ValueError("`y` has classes not in `self.classes_`."
                                 " `self.classes_` has %s. 'y' has %s." %
                                 (self.classes_, classes))

        y = self.label_binarizer_.transform(y)
        return X, y