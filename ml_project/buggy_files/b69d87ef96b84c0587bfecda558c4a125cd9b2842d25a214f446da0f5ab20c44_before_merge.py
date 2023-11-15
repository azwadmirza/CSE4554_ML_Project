def stacked_violin(
    adata: AnnData,
    var_names: Union[_VarNames, Mapping[str, _VarNames]],
    groupby: Union[str, Sequence[str]],
    log: bool = False,
    use_raw: Optional[bool] = None,
    num_categories: int = 7,
    title: Optional[str] = None,
    colorbar_title: Optional[str] = StackedViolin.DEFAULT_COLOR_LEGEND_TITLE,
    figsize: Optional[Tuple[float, float]] = None,
    dendrogram: Union[bool, str] = False,
    gene_symbols: Optional[str] = None,
    var_group_positions: Optional[Sequence[Tuple[int, int]]] = None,
    var_group_labels: Optional[Sequence[str]] = None,
    standard_scale: Optional[Literal['var', 'obs']] = None,
    var_group_rotation: Optional[float] = None,
    layer: Optional[str] = None,
    stripplot: bool = False,
    jitter: Union[float, bool] = False,
    size: int = 1,
    scale: Literal['area', 'count', 'width'] = 'width',
    order: Optional[Sequence[str]] = None,
    swap_axes: bool = False,
    show: Optional[bool] = None,
    save: Union[bool, str, None] = None,
    return_fig: Optional[bool] = False,
    row_palette: Optional[str] = None,
    cmap: Optional[str] = StackedViolin.DEFAULT_COLORMAP,
    ax: Optional[_AxesSubplot] = None,
    **kwds,
) -> Union[StackedViolin, dict, None]:
    """\
    Stacked violin plots.

    Makes a compact image composed of individual violin plots
    (from :func:`~seaborn.violinplot`) stacked on top of each other.
    Useful to visualize gene expression per cluster.

    Wraps :func:`seaborn.violinplot` for :class:`~anndata.AnnData`.

    This function provides a convenient interface to the :class:`StackedViolin`
    class. If you need more flexibility, you should use :class:`StackedViolin` directly.

    Parameters
    ----------
    {common_plot_args}
    {groupby_plots_args}
    stripplot
        Add a stripplot on top of the violin plot.
        See :func:`~seaborn.stripplot`.
    jitter
        Add jitter to the stripplot (only when stripplot is True)
        See :func:`~seaborn.stripplot`.
    size
        Size of the jitter points.
    order
        Order in which to show the categories. Note: if `dendrogram=True`
        the categories order will be given by the dendrogram and `order`
        will be ignored.
    scale
        The method used to scale the width of each violin.
        If 'width' (the default), each violin will have the same width.
        If 'area', each violin will have the same area.
        If 'count', a violin’s width corresponds to the number of observations.
    row_palette
        Be default, median values are mapped to the violin color using a
        color map (see `cmap` argument). Alternatively, a 'row_palette` can
        be given to color each violin plot row using a different colors.
        The value should be a valid seaborn or matplotlib palette name
        (see :func:`~seaborn.color_palette`).
        Alternatively, a single color name or hex value can be passed,
        e.g. `'red'` or `'#cc33ff'`.
    {show_save_ax}
    **kwds
        Are passed to :func:`~seaborn.violinplot`.

    Returns
    -------
    If `return_fig` is `True`, returns a :class:`StackedViolin` object,
    else if `show` is false, return axes dict

    Examples
    -------
    >>> import scanpy as sc
    >>> adata = sc.datasets.pbmc68k_reduced()
    >>> markers = ['C1QA', 'PSAP', 'CD79A', 'CD79B', 'CST3', 'LYZ']
    >>> sc.pl.stacked_violin(adata, markers, groupby='bulk_labels', dendrogram=True)

    Using var_names as dict:
    >>> markers = {{'T-cell': 'CD3D', 'B-cell': 'CD79A', 'myeloid': 'CST3'}}
    >>> sc.pl.stacked_violin(adata, markers, groupby='bulk_labels', dendrogram=True)

    Get StackedViolin object for fine tuning
    >>> vp = sc.pl.stacked_violin(adata, markers, 'bulk_labels', return_fig=True)
    >>> vp.add_totals().style(ylim=(0,5)).show()

    The axes used can be obtained using the get_axes() method
    >>> axes_dict = vp.get_axes()

    See also
    --------
    rank_genes_groups_stacked_violin: to plot marker genes identified using
    the :func:`~scanpy.tl.rank_genes_groups` function.
    """

    vp = StackedViolin(
        adata,
        var_names,
        groupby=groupby,
        use_raw=use_raw,
        log=log,
        num_categories=num_categories,
        standard_scale=standard_scale,
        title=title,
        figsize=figsize,
        gene_symbols=gene_symbols,
        var_group_positions=var_group_positions,
        var_group_labels=var_group_labels,
        var_group_rotation=var_group_rotation,
        layer=layer,
        ax=ax,
        **kwds,
    )

    if dendrogram:
        vp.add_dendrogram(dendrogram_key=dendrogram)
    if swap_axes:
        vp.swap_axes()
    vp = vp.style(
        cmap=cmap,
        stripplot=stripplot,
        jitter=jitter,
        jitter_size=size,
        row_palette=row_palette,
        scale=scale,
    ).legend(title=colorbar_title)
    if return_fig:
        return vp
    else:
        return vp.show(show=show, save=save)