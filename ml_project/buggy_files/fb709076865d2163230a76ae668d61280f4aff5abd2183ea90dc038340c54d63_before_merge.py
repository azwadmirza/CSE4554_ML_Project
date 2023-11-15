    def add_dendrogram(
        self,
        show: Optional[bool] = True,
        dendrogram_key: Optional[str] = None,
        size: Optional[float] = 0.8,
    ):
        """
        Show dendrogram based on the hierarchical clustering between the `groupby`
        categories. Categories are reordered to match the dendrogram order.

        The dendrogram information is computed using :func:`scanpy.tl.dendrogram`.
        If `sc.tl.dendrogram` has not been called previously the function is called
        with default parameters.

        The dendrogram is by default shown on the right side of the plot or on top
        if the axes are swapped.

        `var_names` are reordered to produce a more pleasing output if:
            * The data contains `var_groups`
            * the `var_groups` match the categories.
        The previous conditions happen by default when using Plot
        to show the results from `sc.tl.rank_genes_groups` (aka gene markers), by
        calling `sc.tl.rank_genes_groups_(plot_name)`.

        Parameters
        ----------
        show : bool, default True
        dendrogram_key : str, default None
            Needed if `sc.tl.dendrogram` saved the dendrogram using a key different
            than the default name.
        size : size of the dendrogram. Corresponds to width when dendrogram shown on
            the right of the plot, or height when shown on top.

        Returns
        -------
        BasePlot

        Examples
        --------
        >>> adata = sc.datasets.pbmc68k_reduced()
        >>> markers = {{'T-cell': 'CD3D', 'B-cell': 'CD79A', 'myeloid': 'CST3'}}
        >>> sc.pl.BasePlot(adata, markers, groupby='bulk_labels').add_dendrogram().show()

        """

        if not show:
            self.plot_group_extra = None
            return self

        if self.groupby is None or len(self.categories) <= 2:
            # dendrogram can only be computed  between groupby categories
            logg.warning(
                "Dendrogram not added. Dendrogram is added only "
                "when the number of categories to plot > 2"
            )
            return self

        self.group_extra_size = size

        # to correctly plot the dendrogram the categories need to be ordered
        # according to the dendrogram ordering.
        self._reorder_categories_after_dendrogram(dendrogram_key)

        dendro_ticks = np.arange(len(self.categories)) + 0.5

        self.group_extra_size = size
        self.plot_group_extra = {
            'kind': 'dendrogram',
            'width': size,
            'dendrogram_key': dendrogram_key,
            'dendrogram_ticks': dendro_ticks,
        }
        return self