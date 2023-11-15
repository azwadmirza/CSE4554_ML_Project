    def load(self, filename):
        """Load the results of a previous decomposition and
         demixing analysis from a file.
        Parameters
        ----------
        filename : string
        """
        decomposition = np.load(filename)
        for key, value in decomposition.items():
            if value.dtype == np.dtype('object'):
                value = None
            setattr(self, key, value)
        _logger.info("\n%s loaded correctly" % filename)
        # For compatibility with old version ##################
        if hasattr(self, 'algorithm'):
            self.decomposition_algorithm = self.algorithm
            del self.algorithm
        if hasattr(self, 'V'):
            self.explained_variance = self.V
            del self.V
        if hasattr(self, 'w'):
            self.unmixing_matrix = self.w
            del self.w
        if hasattr(self, 'variance2one'):
            del self.variance2one
        if hasattr(self, 'centered'):
            del self.centered
        if hasattr(self, 'pca_algorithm'):
            self.decomposition_algorithm = self.pca_algorithm
            del self.pca_algorithm
        if hasattr(self, 'ica_algorithm'):
            self.bss_algorithm = self.ica_algorithm
            del self.ica_algorithm
        if hasattr(self, 'v'):
            self.loadings = self.v
            del self.v
        if hasattr(self, 'scores'):
            self.loadings = self.scores
            del self.scores
        if hasattr(self, 'pc'):
            self.loadings = self.pc
            del self.pc
        if hasattr(self, 'ica_scores'):
            self.bss_loadings = self.ica_scores
            del self.ica_scores
        if hasattr(self, 'ica_factors'):
            self.bss_factors = self.ica_factors
            del self.ica_factors
        #
        # Output_dimension is an array after loading, convert it to int
        if hasattr(self, 'output_dimension') and self.output_dimension \
                is not None:
            self.output_dimension = int(self.output_dimension)
        self.summary()