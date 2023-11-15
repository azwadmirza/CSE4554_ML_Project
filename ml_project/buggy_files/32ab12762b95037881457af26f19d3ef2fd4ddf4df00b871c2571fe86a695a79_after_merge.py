    def _fit(self, X, handle_unknown='error'):
        X = self._check_X(X)

        n_samples, n_features = X.shape

        if self._categories != 'auto':
            if X.dtype != object:
                for cats in self._categories:
                    if not np.all(np.sort(cats) == np.array(cats)):
                        raise ValueError("Unsorted categories are not "
                                         "supported for numerical categories")
            if len(self._categories) != n_features:
                raise ValueError("Shape mismatch: if n_values is an array,"
                                 " it has to be of shape (n_features,).")

        self.categories_ = []

        for i in range(n_features):
            Xi = X[:, i]
            if self._categories == 'auto':
                cats = _encode(Xi)
            else:
                cats = np.array(self._categories[i], dtype=X.dtype)
                if handle_unknown == 'error':
                    diff = _encode_check_unknown(Xi, cats)
                    if diff:
                        msg = ("Found unknown categories {0} in column {1}"
                               " during fit".format(diff, i))
                        raise ValueError(msg)
            self.categories_.append(cats)