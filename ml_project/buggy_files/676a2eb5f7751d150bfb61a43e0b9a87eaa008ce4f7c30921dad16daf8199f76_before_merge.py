    def legend(
        self,
        show: Optional[bool] = True,
        title: Optional[str] = DEFAULT_COLOR_LEGEND_TITLE,
        width: Optional[float] = DEFAULT_LEGENDS_WIDTH,
    ):
        """
        Configure legend parameters.

        Parameters
        ----------
        show
            Set to `False` to hide the default plot of the legend.
        title
            Title for the dot size legend. Use "\n" to add line breaks.
        width
            Width of the legend.

        Returns
        -------
        BasePlot

        Examples
        --------
        >>> adata = sc.datasets.pbmc68k_reduced()
        >>> markers = {{'T-cell': 'CD3D', 'B-cell': 'CD79A', 'myeloid': 'CST3'}}
        >>> dp = sc.pl.BasePlot(adata, markers, groupby='bulk_labels')
        >>> dp.legend(colorbar_title='log(UMI counts + 1)').show()
        """

        if not show:
            # turn of legends by setting width to 0
            self.legends_width = 0
        else:
            self.color_legend_title = title
            self.legends_width = width

        return self