    def _reindex_non_unique(self, target):
        """
        Create a new index with target's values (move/add/delete values as
        necessary) use with non-unique Index and a possibly non-unique target.

        Parameters
        ----------
        target : an iterable

        Returns
        -------
        new_index : pd.Index
            Resulting index.
        indexer : np.ndarray or None
            Indices of output values in original index.

        """
        target = ensure_index(target)
        if len(target) == 0:
            # GH#13691
            return self[:0], np.array([], dtype=np.intp), None

        indexer, missing = self.get_indexer_non_unique(target)
        check = indexer != -1
        new_labels = self.take(indexer[check])
        new_indexer = None

        if len(missing):
            length = np.arange(len(indexer))

            missing = ensure_platform_int(missing)
            missing_labels = target.take(missing)
            missing_indexer = ensure_int64(length[~check])
            cur_labels = self.take(indexer[check]).values
            cur_indexer = ensure_int64(length[check])

            new_labels = np.empty((len(indexer),), dtype=object)
            new_labels[cur_indexer] = cur_labels
            new_labels[missing_indexer] = missing_labels

            # GH#38906
            if not len(self):

                new_indexer = np.arange(0)

            # a unique indexer
            elif target.is_unique:

                # see GH5553, make sure we use the right indexer
                new_indexer = np.arange(len(indexer))
                new_indexer[cur_indexer] = np.arange(len(cur_labels))
                new_indexer[missing_indexer] = -1

            # we have a non_unique selector, need to use the original
            # indexer here
            else:

                # need to retake to have the same size as the indexer
                indexer[~check] = -1

                # reset the new indexer to account for the new size
                new_indexer = np.arange(len(self.take(indexer)))
                new_indexer[~check] = -1

        if isinstance(self, ABCMultiIndex):
            new_index = type(self).from_tuples(new_labels, names=self.names)
        else:
            new_index = Index(new_labels, name=self.name)
        return new_index, indexer, new_indexer