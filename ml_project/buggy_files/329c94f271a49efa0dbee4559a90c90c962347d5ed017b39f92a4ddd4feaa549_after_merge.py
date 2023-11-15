    def transform(self, X, y=None):
        """Transform feature->value dicts to array or sparse matrix.

        Named features not encountered during fit or fit_transform will be
        silently ignored.

        Parameters
        ----------
        X : Mapping or iterable over Mappings, length = n_samples
            Dict(s) or Mapping(s) from feature names (arbitrary Python
            objects) to feature values (strings or convertible to dtype).
        y : (ignored)

        Returns
        -------
        Xa : {array, sparse matrix}
            Feature vectors; always 2-d.
        """
        # Sanity check: Python's array has no way of explicitly requesting the
        # signed 32-bit integers that scipy.sparse needs, so we use the next
        # best thing: typecode "i" (int). However, if that gives larger or
        # smaller integers than 32-bit ones, np.frombuffer screws up.
        assert array("i").itemsize == 4, (
            "sizeof(int) != 4 on your platform; please report this at"
            " https://github.com/scikit-learn/scikit-learn/issues and"
            " include the output from platform.platform() in your bug report")

        dtype = self.dtype
        vocab = self.vocabulary_

        if self.sparse:
            X = [X] if isinstance(X, Mapping) else X

            indices = array("i")
            indptr = array("i", [0])
            # XXX we could change values to an array.array as well, but it
            # would require (heuristic) conversion of dtype to typecode...
            values = []

            for x in X:
                for f, v in six.iteritems(x):
                    if isinstance(v, six.string_types):
                        f = "%s%s%s" % (f, self.separator, v)
                        v = 1
                    try:
                        indices.append(vocab[f])
                        values.append(dtype(v))
                    except KeyError:
                        pass

                indptr.append(len(indices))

            if len(indptr) == 0:
                raise ValueError("Sample sequence X is empty.")

            if len(indices) > 0:
                # workaround for bug in older NumPy:
                # http://projects.scipy.org/numpy/ticket/1943
                indices = np.frombuffer(indices, dtype=np.intc)
            indptr = np.frombuffer(indptr, dtype=np.intc)
            shape = (len(indptr) - 1, len(vocab))
            return sp.csr_matrix((values, indices, indptr),
                                 shape=shape, dtype=dtype)

        else:
            X = _tosequence(X)
            Xa = np.zeros((len(X), len(vocab)), dtype=dtype)

            for i, x in enumerate(X):
                for f, v in six.iteritems(x):
                    if isinstance(v, six.string_types):
                        f = "%s%s%s" % (f, self.separator, v)
                        v = 1
                    try:
                        Xa[i, vocab[f]] = dtype(v)
                    except KeyError:
                        pass

            return Xa