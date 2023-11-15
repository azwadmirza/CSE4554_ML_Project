    def _init_umap(self, adata):
        from umap import UMAP

        self._umap = UMAP(metric=adata.uns['neighbors']['params']['metric'])

        self._umap.embedding_ = adata.obsm['X_umap']
        self._umap._raw_data = self._rep
        self._umap._sparse_data = issparse(self._rep)
        self._umap._small_data = self._rep.shape[0] < 4096
        self._umap._metric_kwds = adata.uns['neighbors']['params'].get(
            'metric_kwds', {}
        )
        self._umap._n_neighbors = adata.uns['neighbors']['params']['n_neighbors']
        self._umap._initial_alpha = self._umap.learning_rate

        if self._random_init is not None or self._tree_init is not None:
            self._umap._random_init = self._random_init
            self._umap._tree_init = self._tree_init
            self._umap._search = self._search

        self._umap._rp_forest = self._rp_forest

        self._umap._search_graph = self._search_graph

        self._umap._a = adata.uns['umap']['params']['a']
        self._umap._b = adata.uns['umap']['params']['b']

        self._umap._input_hash = None