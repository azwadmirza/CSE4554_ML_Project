    def add_totals(
        self,
        show: Optional[bool] = True,
        sort: Literal['ascending', 'descending'] = None,
        size: Optional[float] = 0.8,
        color: Optional[Union[ColorLike, Sequence[ColorLike]]] = None,
    ):
        """
        Show barplot for the number of cells in in `groupby` category.

        The barplot is by default shown on the right side of the plot or on top
        if the axes are swapped.

        Parameters
        ----------
        show : bool, default True
        sort : Set to either 'ascending' or 'descending' to reorder the categories
            by cell number
        size : size of the barplot. Corresponds to width when shown on
            the right of the plot, or height when shown on top.
        color: Color for the bar plots or list of colors for each of the bar plots.
            By default, each bar plot uses the colors assigned in `adata.uns[{groupby}_colors.
        Returns
        -------
        BasePlot

        Examples
        --------
        >>> adata = sc.datasets.pbmc68k_reduced()
        >>> markers = {{'T-cell': 'CD3D', 'B-cell': 'CD79A', 'myeloid': 'CST3'}}
        >>> sc.pl.BasePlot(adata, markers, groupby='bulk_labels').add_totals().show()
        """
        self.group_extra_size = size

        if not show:
            # hide totals
            self.plot_group_extra = None
            self.group_extra_size = 0
            return self

        _sort = True if sort is not None else False
        _ascending = True if sort == 'ascending' else False
        counts_df = self.obs_tidy.index.value_counts(sort=_sort, ascending=_ascending)

        if _sort:
            self.categories_order = counts_df.index

        self.plot_group_extra = {
            'kind': 'group_totals',
            'width': size,
            'sort': sort,
            'counts_df': counts_df,
            'color': color,
        }
        return self