    def save(self, fname, protocol=2):
        """Save this NmslibIndexer instance to a file.

        Parameters
        ----------
        fname : str
            Path to the output file,
            will produce 2 files: `fname` - parameters and `fname`.d - :class:`~nmslib.NmslibIndex`.
        protocol : int, optional
            Protocol for pickle.

        Notes
        -----
        This method saves **only** the index (**the model isn't preserved**).

        """
        fname_dict = fname + '.d'
        self.index.saveIndex(fname)
        d = {'index_params': self.index_params, 'query_time_params': self.query_time_params, 'labels': self.labels}
        with open(fname_dict, 'wb') as fout:
            _pickle.dump(d, fout, protocol=protocol)