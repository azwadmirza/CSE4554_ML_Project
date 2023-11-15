    def save(self, fname, protocol=2):
        """Save AnnoyIndexer instance to disk.

        Parameters
        ----------
        fname : str
            Path to output. Save will produce 2 files:
            `fname`: Annoy index itself.
            `fname.dict`: Index metadata.
        protocol : int, optional
            Protocol for pickle.

        Notes
        -----
        This method saves **only the index**. The trained model isn't preserved.

        """
        self.index.save(fname)
        d = {'f': self.model.vector_size, 'num_trees': self.num_trees, 'labels': self.labels}
        with utils.open(fname + '.dict', 'wb') as fout:
            _pickle.dump(d, fout, protocol=protocol)