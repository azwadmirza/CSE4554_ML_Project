    def style(
        self,
        cmap: str = DEFAULT_COLORMAP,
        stripplot: Optional[bool] = DEFAULT_STRIPPLOT,
        jitter: Optional[Union[float, bool]] = DEFAULT_JITTER,
        jitter_size: Optional[int] = DEFAULT_JITTER_SIZE,
        linewidth: Optional[float] = DEFAULT_LINE_WIDTH,
        row_palette: Optional[str] = DEFAULT_ROW_PALETTE,
        scale: Optional[Literal['area', 'count', 'width']] = DEFAULT_SCALE,
        yticklabels: Optional[bool] = DEFAULT_PLOT_YTICKLABELS,
        ylim: Optional[Tuple[float, float]] = DEFAULT_YLIM,
    ):
        """\
        Modifies plot visual parameters

        Parameters
        ----------
        cmap
            String denoting matplotlib color map.
        stripplot
            Add a stripplot on top of the violin plot.
            See :func:`~seaborn.stripplot`.
        jitter
            Add jitter to the stripplot (only when stripplot is True)
            See :func:`~seaborn.stripplot`.
        jitter_size
            Size of the jitter points.
        linewidth
            linewidth for the violin plots.
        row_palette
            The row palette determines the colors to use for the stacked violins.
            The value should be a valid seaborn or matplotlib palette name
            (see :func:`~seaborn.color_palette`).
            Alternatively, a single color name or hex value can be passed,
            e.g. `'red'` or `'#cc33ff'`.
        scale
            The method used to scale the width of each violin.
            If 'width' (the default), each violin will have the same width.
            If 'area', each violin will have the same area.
            If 'count', a violin’s width corresponds to the number of observations.
        yticklabels
            Because the plots are on top of each other the yticks labels tend to
            overlap and are not plotted. Set to true to view the labels.
        ylim
            minimum and maximum values for the y-axis. If set. All rows will have
            the same y-axis range. Example: ylim=(0, 5)

        Returns
        -------
        :class:`~scanpy.pl.StackedViolin`

        Examples
        -------
        >>> adata = sc.datasets.pbmc68k_reduced()
        >>> markers = ['C1QA', 'PSAP', 'CD79A', 'CD79B', 'CST3', 'LYZ']

        Change color map and turn off edges

        >>> sc.pl.MatrixPlot(adata, markers, groupby='bulk_labels')\
        ...               .style(row_palette='Blues', linewidth=0).show()

        """

        self.cmap = cmap
        self.row_palette = row_palette
        self.kwds['color'] = self.row_palette
        self.stripplot = stripplot
        self.jitter = jitter
        self.jitter_size = jitter_size
        self.plot_yticklabels = yticklabels
        self.ylim = ylim

        self.kwds['linewidth'] = linewidth
        self.kwds['scale'] = scale

        return self