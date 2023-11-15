def _setup_extra_categorical_covs(
    adata: anndata.AnnData,
    categorical_covariate_keys: List[str],
    category_dict: Dict[str, List[str]] = None,
):
    """
    Setup obsm df for extra categorical covariates.

    Parameters
    ----------
    adata
        AnnData to setup
    categorical_covariate_keys
        List of keys in adata.obs with categorical data
    category_dict
        Optional dictionary with keys being keys of categorical data in obs
        and values being precomputed categories for each obs vector

    """
    for key in categorical_covariate_keys:
        _assert_key_in_obs(adata, key)

    cat_loc = "obsm"
    cat_key = "_scvi_extra_categoricals"

    one_hots = []

    categories = {}
    for key in categorical_covariate_keys:
        cat = adata.obs[key]
        if category_dict is not None:
            possible_cats = category_dict[key]
            cat = cat.astype(CategoricalDtype(categories=possible_cats))
        else:
            categories[key] = cat.astype("category").cat.categories.to_numpy(copy=True)

        one_hot_rep = pd.get_dummies(cat, prefix=key)
        one_hots.append(one_hot_rep)

    adata.obsm[cat_key] = pd.concat(one_hots, axis=1)

    store_cats = categories if category_dict is None else category_dict
    adata.uns["_scvi"]["extra_categorical_mappings"] = store_cats
    return cat_loc, cat_key