    def style(
        self,
        cmap: str = DEFAULT_COLORMAP,
        edge_color: Optional[ColorLike] = DEFAULT_EDGE_COLOR,
        edge_lw: Optional[float] = DEFAULT_EDGE_LW,
    ):
        """
        Modifies plot graphical parameters

        Parameters
        ----------
        cmap
            String denoting matplotlib color map.
        edge_color
            Edge color betweem the squares of matrix plot. Default is gray
        edge_lw
            Edge line width.

        Returns
        -------
        MatrixPlot

        Examples
        -------
        >>> adata = sc.datasets.pbmc68k_reduced()
        >>> markers = ['C1QA', 'PSAP', 'CD79A', 'CD79B', 'CST3', 'LYZ']

        Change color map and turn off edges
        >>> sc.pl.MatrixPlot(adata, markers, groupby='bulk_labels')\
        ...               .style(cmap='Blues', edge_color='none').show()

        """

        self.cmap = cmap
        self.edge_color = edge_color
        self.edge_lw = edge_lw

        return self