    def reindex(self, target, method=None, level=None, limit=None,
                tolerance=None):
        """
        Create index with target's values (move/add/delete values as necessary)

        Returns
        -------
        new_index : pd.Index
            Resulting index
        indexer : np.ndarray or None
            Indices of output values in original index

        """

        if method is not None:
            raise NotImplementedError("argument method is not implemented for "
                                      "CategoricalIndex.reindex")
        if level is not None:
            raise NotImplementedError("argument level is not implemented for "
                                      "CategoricalIndex.reindex")
        if limit is not None:
            raise NotImplementedError("argument limit is not implemented for "
                                      "CategoricalIndex.reindex")

        target = ibase._ensure_index(target)

        if not is_categorical_dtype(target) and not target.is_unique:
            raise ValueError("cannot reindex with a non-unique indexer")

        indexer, missing = self.get_indexer_non_unique(np.array(target))

        if len(self.codes):
            new_target = self.take(indexer)
        else:
            new_target = target

        # filling in missing if needed
        if len(missing):
            cats = self.categories.get_indexer(target)

            if (cats == -1).any():
                # coerce to a regular index here!
                result = Index(np.array(self), name=self.name)
                new_target, indexer, _ = result._reindex_non_unique(
                    np.array(target))
            else:

                codes = new_target.codes.copy()
                codes[indexer == -1] = cats[missing]
                new_target = self._create_from_codes(codes)

        # we always want to return an Index type here
        # to be consistent with .reindex for other index types (e.g. they don't
        # coerce based on the actual values, only on the dtype)
        # unless we had an inital Categorical to begin with
        # in which case we are going to conform to the passed Categorical
        new_target = np.asarray(new_target)
        if is_categorical_dtype(target):
            new_target = target._shallow_copy(new_target, name=self.name)
        else:
            new_target = Index(new_target, name=self.name)

        return new_target, indexer