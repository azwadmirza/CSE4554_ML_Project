    def __init__(self, data, ncomp=None, standardize=True, demean=True,
                 normalize=True, gls=False, weights=None, method='svd',
                 missing=None, tol=5e-8, max_iter=1000, tol_em=5e-8,
                 max_em_iter=100, ):
        self._index = None
        self._columns = []
        if isinstance(data, pd.DataFrame):
            self._index = data.index
            self._columns = data.columns

        self.data = np.asarray(data)
        # Store inputs
        self._gls = gls
        self._normalize = normalize
        self._tol = tol
        if not 0 < self._tol < 1:
            raise ValueError('tol must be strictly between 0 and 1')
        self._max_iter = max_iter
        self._max_em_iter = max_em_iter
        self._tol_em = tol_em

        # Prepare data
        self._standardize = standardize
        self._demean = demean

        self._nobs, self._nvar = self.data.shape
        if weights is None:
            weights = np.ones(self._nvar)
        else:
            weights = np.array(weights).flatten()
            if weights.shape[0] != self._nvar:
                raise ValueError('weights should have nvar elements')
            weights = weights / np.sqrt((weights ** 2.0).mean())
        self.weights = weights

        # Check ncomp against maximum
        min_dim = min(self._nobs, self._nvar)
        self._ncomp = min_dim if ncomp is None else ncomp
        if self._ncomp > min_dim:
            import warnings

            warn = 'The requested number of components is more than can be ' \
                   'computed from data. The maximum number of components is ' \
                   'the minimum of the number of observations or variables'
            warnings.warn(warn, ValueWarning)
            self._ncomp = min_dim

        self._method = method
        if self._method == 'eig':
            self._compute_eig = self._compute_using_eig
        elif self._method == 'svd':
            self._compute_eig = self._compute_using_svd
        elif self._method == 'nipals':
            self._compute_eig = self._compute_using_nipals
        else:
            raise ValueError('method is not known.')

        self.rows = np.arange(self._nobs)
        self.cols = np.arange(self._nvar)
        # Handle missing
        self._missing = missing
        self._adjusted_data = self.data
        if missing is not None:
            self._adjust_missing()
            # Update size
            self._nobs, self._nvar = self._adjusted_data.shape
            if self._ncomp == np.min(self.data.shape):
                self._ncomp = np.min(self._adjusted_data.shape)
            elif self._ncomp > np.min(self._adjusted_data.shape):
                raise ValueError('When adjusting for missing values, user '
                                 'provided ncomp must be no larger than the '
                                 'smallest dimension of the '
                                 'missing-value-adjusted data size.')

        # Attributes and internal values
        self._tss = 0.0
        self._ess = None
        self.transformed_data = None
        self._mu = None
        self._sigma = None
        self._ess_indiv = None
        self._tss_indiv = None
        self.scores = self.factors = None
        self.loadings = None
        self.coeff = None
        self.eigenvals = None
        self.eigenvecs = None
        self.projection = None
        self.rsquare = None
        self.ic = None

        # Prepare data
        self.transformed_data = self._prepare_data()
        # Perform the PCA
        self._pca()
        if gls:
            self._compute_gls_weights()
            self.transformed_data = self._prepare_data()
            self._pca()

        # Final calculations
        self._compute_rsquare_and_ic()
        if self._index is not None:
            self._to_pandas()