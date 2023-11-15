    def save(
            self, fname_or_handle,
            separately=None, sep_limit=10 * 1024**2, ignore=frozenset(), pickle_protocol=PICKLE_PROTOCOL,
        ):
        """Save the object to a file.

        Parameters
        ----------
        fname_or_handle : str or file-like
            Path to output file or already opened file-like object. If the object is a file handle,
            no special array handling will be performed, all attributes will be saved to the same file.
        separately : list of str or None, optional
            If None, automatically detect large numpy/scipy.sparse arrays in the object being stored, and store
            them into separate files. This prevent memory errors for large objects, and also allows
            `memory-mapping <https://en.wikipedia.org/wiki/Mmap>`_ the large arrays for efficient
            loading and sharing the large arrays in RAM between multiple processes.

            If list of str: store these attributes into separate files. The automated size check
            is not performed in this case.
        sep_limit : int, optional
            Don't store arrays smaller than this separately. In bytes.
        ignore : frozenset of str, optional
            Attributes that shouldn't be stored at all.
        pickle_protocol : int, optional
            Protocol number for pickle.

        See Also
        --------
        :meth:`~gensim.utils.SaveLoad.load`
            Load object from file.

        """
        self.add_lifecycle_event(
            "saving",
            fname_or_handle=str(fname_or_handle),
            separately=str(separately),
            sep_limit=sep_limit,
            ignore=ignore,
        )
        try:
            _pickle.dump(self, fname_or_handle, protocol=pickle_protocol)
            logger.info("saved %s object", self.__class__.__name__)
        except TypeError:  # `fname_or_handle` does not have write attribute
            self._smart_save(fname_or_handle, separately, sep_limit, ignore, pickle_protocol=pickle_protocol)