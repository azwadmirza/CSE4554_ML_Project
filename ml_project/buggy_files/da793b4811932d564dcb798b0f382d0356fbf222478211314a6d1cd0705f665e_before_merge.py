    def extract_data_from_anndata(self, ad: anndata.AnnData):
        data, gene_names, batch_indices, cell_types, labels = None, None, None, None, None
        self.obs = (
            ad.obs
        )  # provide access to observation annotations from the underlying AnnData object.

        if isinstance(ad.X, np.ndarray):
            data = ad.X.copy()  # Dense
        else:
            data = ad.X.toarray()  # Sparse

        select = data.sum(axis=1) > 0  # Take out cells that doesn't express any gene
        data = data[select, :]

        gene_names = np.array(ad.var.index.values, dtype=str)

        if 'batch_indices' in self.obs.columns:
            batch_indices = self.obs['batch_indices'].values

        if 'cell_types' in self.obs.columns:
            cell_types = self.obs['cell_types']
            cell_types = cell_types.drop_duplicates().values.astype('str')

        if 'labels' in self.obs.columns:
            labels = self.obs['labels']
        elif 'cell_types' in self.obs.columns:
            labels = self.obs['cell_types'].rank(method='dense').values.astype('int')

        return data, gene_names, batch_indices, cell_types, labels