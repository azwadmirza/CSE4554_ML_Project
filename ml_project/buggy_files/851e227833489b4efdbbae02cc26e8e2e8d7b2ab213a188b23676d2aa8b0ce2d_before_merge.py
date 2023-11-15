    def __init__(
        self,
        filename_or_anndata,
        save_path="data/",
        url=None,
        new_n_genes=False,
        subset_genes=None,
    ):
        """

        """

        if type(filename_or_anndata) == str:
            self.download_name = filename_or_anndata
            self.save_path = save_path
            self.url = url

            data, gene_names, batch_indices, cell_types, labels = self.download_and_preprocess()

        elif isinstance(filename_or_anndata, anndata.AnnData):
            ad = filename_or_anndata
            data, gene_names, batch_indices, cell_types, labels = self.extract_data_from_anndata(ad)

        else:
            raise Exception(
                "Please provide a filename of an AnnData file or an already loaded AnnData object"
            )

        X, local_means, local_vars, batch_indices_, labels = \
            GeneExpressionDataset.get_attributes_from_matrix(data, labels=labels)
        batch_indices = batch_indices if batch_indices is not None else batch_indices_

        super().__init__(X, local_means, local_vars, batch_indices, labels,
                         gene_names=gene_names, cell_types=cell_types)

        self.subsample_genes(new_n_genes=new_n_genes, subset_genes=subset_genes)