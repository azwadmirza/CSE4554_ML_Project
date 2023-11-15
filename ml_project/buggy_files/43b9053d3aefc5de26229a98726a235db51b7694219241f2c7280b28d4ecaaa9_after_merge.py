    def compute_neighbors(
        self,
        n_neighbors: int = 30,
        knn: bool = True,
        n_pcs: Optional[int] = None,
        use_rep: Optional[str] = None,
        method: _Method = 'umap',
        random_state: AnyRandom = 0,
        write_knn_indices: bool = False,
        metric: _Metric = 'euclidean',
        metric_kwds: Mapping[str, Any] = MappingProxyType({}),
    ) -> None:
        """\
        Compute distances and connectivities of neighbors.

        Parameters
        ----------
        n_neighbors
             Use this number of nearest neighbors.
        knn
             Restrict result to `n_neighbors` nearest neighbors.
        {n_pcs}
        {use_rep}

        Returns
        -------
        Writes sparse graph attributes `.distances` and `.connectivities`.
        Also writes `.knn_indices` and `.knn_distances` if
        `write_knn_indices==True`.
        """
        from sklearn.metrics import pairwise_distances
        start_neighbors = logg.debug('computing neighbors')
        if n_neighbors > self._adata.shape[0]:  # very small datasets
            n_neighbors = 1 + int(0.5*self._adata.shape[0])
            logg.warning(f'n_obs too small: adjusting to `n_neighbors = {n_neighbors}`')
        if method == 'umap' and not knn:
            raise ValueError('`method = \'umap\' only with `knn = True`.')
        if method == 'rapids' and metric != 'euclidean':
            raise ValueError("`method` 'rapids' only supports the 'euclidean' `metric`.")
        if method not in {'umap', 'gauss', 'rapids'}:
            raise ValueError("`method` needs to be 'umap', 'gauss', or 'rapids'.")
        if self._adata.shape[0] >= 10000 and not knn:
            logg.warning('Using high n_obs without `knn=True` takes a lot of memory...')
        self.n_neighbors = n_neighbors
        self.knn = knn
        X = _choose_representation(self._adata, use_rep=use_rep, n_pcs=n_pcs)
        # neighbor search
        use_dense_distances = (metric == 'euclidean' and X.shape[0] < 8192) or knn == False
        if use_dense_distances:
            _distances = pairwise_distances(X, metric=metric, **metric_kwds)
            knn_indices, knn_distances = _get_indices_distances_from_dense_matrix(
                _distances, n_neighbors)
            if knn:
                self._distances = _get_sparse_matrix_from_indices_distances_numpy(
                    knn_indices, knn_distances, X.shape[0], n_neighbors)
            else:
                self._distances = _distances
        elif method == 'rapids':
            knn_indices, knn_distances = compute_neighbors_rapids(X, n_neighbors)
        else:
            # non-euclidean case and approx nearest neighbors
            if X.shape[0] < 4096:
                X = pairwise_distances(X, metric=metric, **metric_kwds)
                metric = 'precomputed'
            knn_indices, knn_distances, forest = compute_neighbors_umap(
                X, n_neighbors, random_state, metric=metric, metric_kwds=metric_kwds)
            # very cautious here
            try:
                if forest:
                    self._rp_forest = _make_forest_dict(forest)
            except:
                pass
        # write indices as attributes
        if write_knn_indices:
            self.knn_indices = knn_indices
            self.knn_distances = knn_distances
        start_connect = logg.debug('computed neighbors', time=start_neighbors)
        if not use_dense_distances or method in {'umap', 'rapids'}:
            # we need self._distances also for method == 'gauss' if we didn't
            # use dense distances
            self._distances, self._connectivities = _compute_connectivities_umap(
                knn_indices,
                knn_distances,
                self._adata.shape[0],
                self.n_neighbors,
            )
        # overwrite the umap connectivities if method is 'gauss'
        # self._distances is unaffected by this
        if method == 'gauss':
            self._compute_connectivities_diffmap()
        logg.debug('computed connectivities', time=start_connect)
        self._number_connected_components = 1
        if issparse(self._connectivities):
            from scipy.sparse.csgraph import connected_components
            self._connected_components = connected_components(self._connectivities)
            self._number_connected_components = self._connected_components[0]