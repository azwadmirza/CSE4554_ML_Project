def get_from_registry(adata: anndata.AnnData, key: str) -> np.ndarray:
    """
    Returns the object in AnnData associated with the key in ``.uns['_scvi']['data_registry']``.

    Parameters
    ----------
    adata
        anndata object already setup with `scvi.data.setup_anndata()`
    key
        key of object to get from ``adata.uns['_scvi]['data_registry']``

    Returns
    -------
    The requested data

    Examples
    --------
    >>> import scvi
    >>> adata = scvi.data.cortex()
    >>> adata.uns['_scvi']['data_registry']
    {'X': ['_X', None],
    'batch_indices': ['obs', 'batch'],
    'local_l_mean': ['obs', '_scvi_local_l_mean'],
    'local_l_var': ['obs', '_scvi_local_l_var'],
    'labels': ['obs', 'labels']}
    >>> batch = get_from_registry(adata, "batch_indices")
    >>> batch
    array([[0],
           [0],
           [0],
           ...,
           [0],
           [0],
           [0]])
    """
    data_loc = adata.uns["_scvi"]["data_registry"][key]
    attr_name, attr_key = data_loc["attr_name"], data_loc["attr_key"]

    data = getattr(adata, attr_name)
    if attr_key != "None":
        if isinstance(data, pd.DataFrame):
            data = data.loc[:, attr_key]
        else:
            data = data[attr_key]
    if isinstance(data, pd.Series):
        data = data.to_numpy().reshape(-1, 1)
    return data