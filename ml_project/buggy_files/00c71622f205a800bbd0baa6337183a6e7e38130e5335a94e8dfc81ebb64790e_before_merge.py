def matrixplot(
    adata: AnnData,
    var_names: Union[_VarNames, Mapping[str, _VarNames]],
    groupby: Union[str, Sequence[str]],
    use_raw: Optional[bool] = None,
    log: bool = False,
    num_categories: int = 7,
    figsize: Optional[Tuple[float, float]] = None,
    dendrogram: Union[bool, str] = False,
    title: Optional[str] = None,
    cmap: Optional[str] = MatrixPlot.DEFAULT_COLORMAP,
    colorbar_title: Optional[str] = MatrixPlot.DEFAULT_COLOR_LEGEND_TITLE,
    gene_symbols: Optional[str] = None,
    var_group_positions: Optional[Sequence[Tuple[int, int]]] = None,
    var_group_labels: Optional[Sequence[str]] = None,
    var_group_rotation: Optional[float] = None,
    layer: Optional[str] = None,
    standard_scale: Literal['var', 'group'] = None,
    values_df: Optional[pd.DataFrame] = None,
    swap_axes: bool = False,
    show: Optional[bool] = None,
    save: Union[str, bool, None] = None,
    ax: Optional[_AxesSubplot] = None,
    return_fig: Optional[bool] = False,
    **kwds,
) -> Union[MatrixPlot, dict, None]:
    """\
    Creates a heatmap of the mean expression values per cluster of each var_names.

    This function provides a convenient interface to the :class:`MatrixPlot`
    class. If you need more flexibility, you should use :class:`MatrixPlot` directly.

    Parameters
    ----------
    {common_plot_args}
    {groupby_plots_args}
    {show_save_ax}
    **kwds
        Are passed to :func:`matplotlib.pyplot.pcolor`.

    Returns
    -------
    if `show` is `False`, returns a :class:`MatrixPlot` object

    Examples
    --------
    >>> import scanpy as sc
    >>> adata = sc.datasets.pbmc68k_reduced()
    >>> markers = ['C1QA', 'PSAP', 'CD79A', 'CD79B', 'CST3', 'LYZ']
    >>> sc.pl.matrixplot(adata, markers, groupby='bulk_labels', dendrogram=True)

    Using var_names as dict:
    >>> markers = {{'T-cell': 'CD3D', 'B-cell': 'CD79A', 'myeloid': 'CST3'}}
    >>> sc.pl.matrixplot(adata, markers, groupby='bulk_labels', dendrogram=True)

    Get Matrix object for fine tuning
    >>> mp = sc.pl.matrix(adata, markers, 'bulk_labels', return_fig=True)
    >>> mp.add_totals().style(edge_color='black').show()

    The axes used can be obtained using the get_axes() method
    >>> axes_dict = mp.get_axes()

    See also
    --------
    :func:`~scanpy.pl.rank_genes_groups_matrixplot`: to plot marker genes
    identified using the :func:`~scanpy.tl.rank_genes_groups` function.
    """

    mp = MatrixPlot(
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
        values_df=values_df,
        ax=ax,
        **kwds,
    )

    if dendrogram:
        mp.add_dendrogram(dendrogram_key=dendrogram)
    if swap_axes:
        mp.swap_axes()

    mp = mp.style(cmap=cmap).legend(title=colorbar_title)
    if return_fig:
        return mp
    else:
        return mp.show(show=show, save=save)