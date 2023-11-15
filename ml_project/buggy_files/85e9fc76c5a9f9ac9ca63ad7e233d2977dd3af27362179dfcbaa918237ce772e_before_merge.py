    def _partial_fit(self, X, y, classes=None):
        _check_partial_fit_first_call(self, classes)

        super(MLPClassifier, self)._partial_fit(X, y)

        return self