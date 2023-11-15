def var_df(
    adata: AnnData,
    keys: Iterable[str] = (),
    varm_keys: Iterable[Tuple[str, int]] = (),
    *,
    layer: str = None,
) -> pd.DataFrame:
    """\
    Return values for observations in adata.

    Params
    ------
    adata
        AnnData object to get values from.
    keys
        Keys from either `.obs_names`, or `.var.columns`.
    varm_keys
        Tuple of `(key from varm, column index of varm[key])`.
    layer
        Layer of `adata` to use as expression values.

    Returns
    -------
    A dataframe with `adata.var_names` as index, and values specified by `keys`
    and `varm_keys`.
    """
    # Argument handling
    var_cols, obs_idx_keys, _ = _check_indices(adata.var, adata.obs_names, "var", keys)

    # initialize df
    df = pd.DataFrame(index=adata.var.index)

    if len(obs_idx_keys) > 0:
        matrix = _get_array_values(
            _get_obs_rep(adata, layer=layer),
            adata.obs_names,
            obs_idx_keys,
            axis=0,
            backed=adata.isbacked,
        ).T
        df = pd.concat(
            [df, pd.DataFrame(matrix, columns=obs_idx_keys, index=adata.var_names)],
            axis=1,
        )

    # add obs values
    if len(var_cols) > 0:
        df = pd.concat([df, adata.var[var_cols]], axis=1)

    # reorder columns to given order
    if keys:
        df = df[keys]

    for k, idx in varm_keys:
        added_k = f"{k}-{idx}"
        val = adata.varm[k]
        if isinstance(val, np.ndarray):
            df[added_k] = np.ravel(val[:, idx])
        elif isinstance(val, spmatrix):
            df[added_k] = np.ravel(val[:, idx].toarray())
        elif isinstance(val, pd.DataFrame):
            df[added_k] = val.loc[:, idx]
    return df