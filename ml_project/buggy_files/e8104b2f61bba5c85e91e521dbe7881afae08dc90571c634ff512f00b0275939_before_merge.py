def recipe_weinreb17(
    adata: AnnData,
    log: bool = True,
    mean_threshold: float = 0.01,
    cv_threshold: int = 2,
    n_pcs: int = 50,
    svd_solver='randomized',
    random_state: Union[int, RandomState] = 0,
    copy: bool = False,
) -> Optional[AnnData]:
    """\
    Normalization and filtering as of [Weinreb17]_.

    Expects non-logarithmized data.
    If using logarithmized data, pass `log=False`.

    Parameters
    ----------
    adata
        Annotated data matrix.
    log
        Logarithmize data?
    copy
        Return a copy if true.
    """
    from scipy.sparse import issparse
    if issparse(adata.X):
        raise ValueError('`recipe_weinreb16 does not support sparse matrices.')
    if copy: adata = adata.copy()
    if log: pp.log1p(adata)
    adata.X = pp.normalize_per_cell_weinreb16_deprecated(
        adata.X, max_fraction=0.05, mult_with_mean=True
    )
    gene_subset = filter_genes_cv_deprecated(
        adata.X, mean_threshold, cv_threshold
    )
    adata._inplace_subset_var(gene_subset)  # this modifies the object itself
    X_pca = pp.pca(
        pp.zscore_deprecated(adata.X),
        n_comps=n_pcs,
        svd_solver=svd_solver,
        random_state=random_state,
    )
    # update adata
    adata.obsm['X_pca'] = X_pca
    return adata if copy else None