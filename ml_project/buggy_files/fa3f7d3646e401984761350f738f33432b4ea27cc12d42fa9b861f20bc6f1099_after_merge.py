def _make_obs_column_categorical(
    adata, column_key, alternate_column_key, categorical_dtype=None
):
    """
    Makes the data in column_key in obs all categorical.

    If adata.obs[column_key] is not categorical, will categorize
    and save to .obs[alternate_column_key]
    """
    if categorical_dtype is None:
        categorical_obs = adata.obs[column_key].astype("category")
    else:
        categorical_obs = adata.obs[column_key].astype(categorical_dtype)

    # put codes in .obs[alternate_column_key]
    codes = categorical_obs.cat.codes
    mapping = categorical_obs.cat.categories.to_numpy(copy=True)
    if -1 in np.unique(codes):
        received_categories = adata.obs[column_key].astype("category").cat.categories
        raise ValueError(
            'Making .obs["{}"] categorical failed. Expected categories: {}. '
            "Received categories: {}. ".format(column_key, mapping, received_categories)
        )
    adata.obs[alternate_column_key] = codes

    # store categorical mappings
    store_dict = {
        alternate_column_key: {"original_key": column_key, "mapping": mapping}
    }
    if "categorical_mappings" not in adata.uns["_scvi"].keys():
        adata.uns["_scvi"].update({"categorical_mappings": store_dict})
    else:
        adata.uns["_scvi"]["categorical_mappings"].update(store_dict)

    # make sure each category contains enough cells
    unique, counts = np.unique(adata.obs[alternate_column_key], return_counts=True)
    if np.min(counts) < 3:
        category = unique[np.argmin(counts)]
        warnings.warn(
            "Category {} in adata.obs['{}'] has fewer than 3 cells. SCVI may not train properly.".format(
                category, alternate_column_key
            )
        )
    # possible check for continuous?
    if len(unique) > (adata.shape[0] / 3):
        warnings.warn(
            "Is adata.obs['{}'] continuous? SCVI doesn't support continuous obs yet."
        )
    return alternate_column_key