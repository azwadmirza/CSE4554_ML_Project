def _enrich_anndata(
    adata: AnnData,
    group: str,
    *,
    org: Optional[str] = "hsapiens",
    key: str = "rank_genes_groups",
    pval_cutoff: float = 0.05,
    log2fc_min: Optional[float] = None,
    log2fc_max: Optional[float] = None,
    gene_symbols: Optional[str] = None,
    gprofiler_kwargs: Mapping[str, Any] = MappingProxyType({}),
) -> pd.DataFrame:
    de = rank_genes_groups_df(
        adata,
        group=group,
        key=key,
        pval_cutoff=pval_cutoff,
        log2fc_min=log2fc_min,
        log2fc_max=log2fc_max,
        gene_symbols=gene_symbols,
    )
    if gene_symbols is not None:
        gene_list = list(de[gene_symbols])
    else:
        gene_list = list(de["names"])
    return enrich(gene_list, org=org, gprofiler_kwargs=gprofiler_kwargs)