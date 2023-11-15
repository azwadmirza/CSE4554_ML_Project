def enrich(
    container: Iterable[str],
    *,
    org: str = "hsapiens",
    gprofiler_kwargs: Mapping[str, Any] = MappingProxyType({}),
) -> pd.DataFrame:
    """\
    Get enrichment for DE results.

    This is a thin convenience wrapper around the very useful gprofiler_.

    This method dispatches on the first argument, leading to the following two
    signatures::

        enrich(container, ...)
        enrich(adata: AnnData, group, key: str, ...)

    Where::

        enrich(adata, group, key, ...) = enrich(adata.uns[key]["names"][group], ...)

    .. _gprofiler: https://pypi.org/project/gprofiler-official/#description

    Parameters
    ----------
    container
        Contains genes you'd like to search.
    adata
        AnnData object whose group will be looked for.
    group
        The group whose genes should be used for enrichment.
    key
        Key in `uns` to find group under.
    {doc_org}
    gprofiler_kwargs
        Keyword arguments to pass to `GProfiler.profile`, see gprofiler_.

    Returns
    -------
    Dataframe of enrichment results.

    Examples
    --------
    Using `sc.queries.enrich` on a list of genes:

    >>> import scanpy as sc
    >>> sc.queries.enrich(['Klf4', 'Pax5', 'Sox2', 'Nanog'], org="hsapiens")

    Using `sc.queries.enrich` on an :class:`anndata.AnnData` object:

    >>> pbmcs = sc.datasets.pbmc68k_reduced()
    >>> sc.tl.rank_genes_groups(pbmcs, "bulk_labels")
    >>> sc.queries.enrich(pbmcs, "CD34+")
    """
    try:
        from gprofiler import GProfiler
    except ImportError:
        raise ImportError(
            "This method requires the `gprofiler-official` module to be installed."
        )
    gprofiler = GProfiler(user_agent="scanpy", return_dataframe=True)
    gprofiler_kwargs = dict(gprofiler_kwargs)
    for k in ["organism"]:
        if gprofiler_kwargs.get(k) is not None:
            raise ValueError(
                f"Argument `{k}` should be passed directly through `enrich`, "
                "not through `gprofiler_kwargs`"
            )
    return gprofiler.profile(list(container), organism=org, **gprofiler_kwargs)