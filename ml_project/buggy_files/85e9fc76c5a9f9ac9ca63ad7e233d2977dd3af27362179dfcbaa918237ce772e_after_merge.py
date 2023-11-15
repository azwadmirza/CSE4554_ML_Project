    def _partial_fit(self, X, y, classes=None):
        if _check_partial_fit_first_call(self, classes):
            self._label_binarizer = LabelBinarizer()
            if type_of_target(y).startswith('multilabel'):
                self._label_binarizer.fit(y)
            else:
                self._label_binarizer.fit(classes)

        super(MLPClassifier, self)._partial_fit(X, y)

        return self