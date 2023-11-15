def recipe_seurat(
    adata: AnnData,
    log: bool = True,
    plot: bool = False,
    copy: bool = False,
) -> Optional[AnnData]:
    """\
    Normalization and filtering as of Seurat [Satija15]_.

    This uses a particular preprocessing.

    Expects non-logarithmized data.
    If using logarithmized data, pass `log=False`.
    """
    if copy: adata = adata.copy()
    pp.filter_cells(adata, min_genes=200)
    pp.filter_genes(adata, min_cells=3)
    normalize_total(adata, target_sum=1e4)
    filter_result = filter_genes_dispersion(
        adata.X, min_mean=0.0125, max_mean=3, min_disp=0.5, log=not log)
    if plot:
        from ..plotting import _preprocessing as ppp  # should not import at the top of the file
        ppp.filter_genes_dispersion(filter_result, log=not log)
    adata._inplace_subset_var(filter_result.gene_subset)  # filter genes
    if log: pp.log1p(adata)
    pp.scale(adata, max_value=10)
    return adata if copy else None