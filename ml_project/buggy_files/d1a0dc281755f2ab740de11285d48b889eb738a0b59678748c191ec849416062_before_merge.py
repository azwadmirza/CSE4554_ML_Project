def transfer_anndata_setup(
    adata_source: Union[anndata.AnnData, dict], adata_target: anndata.AnnData
):
    """
    Transfer anndata setup from a source object to a target object.

    This handles encoding for categorical data and is useful in the case where an
    anndata object has been subsetted and a category is lost.

    Parameters
    ----------
    adata_source
        AnnData that has been setup with scvi. If `dict`, must be dictionary
        from source anndata containing scvi setup parameters.
    adata_target
        AnnData with equivalent organization as source, but possibly subsetted.
    """
    adata_target.uns["_scvi"] = {}

    if isinstance(adata_source, anndata.AnnData):
        _scvi_dict = adata_source.uns["_scvi"]
    else:
        _scvi_dict = adata_source
    data_registry = _scvi_dict["data_registry"]
    summary_stats = _scvi_dict["summary_stats"]

    # transfer version
    adata_target.uns["_scvi"]["scvi_version"] = _scvi_dict["scvi_version"]

    x_loc = data_registry[_CONSTANTS.X_KEY]["attr_name"]
    if x_loc == "layers":
        layer = data_registry[_CONSTANTS.X_KEY]["attr_key"]
    else:
        layer = None

    if _scvi_dict["use_raw"] is True:
        adata_target.uns["_scvi"]["use_raw"] = True
        use_raw = True
    else:
        adata_target.uns["_scvi"]["use_raw"] = False
        use_raw = False

    target_n_vars = adata_target.shape[1] if not use_raw else adata_target.raw.shape[1]
    if target_n_vars != summary_stats["n_vars"]:
        raise ValueError(
            "Number of vars in adata_target not the same as source. "
            + "Expected: {} Received: {}".format(target_n_vars, summary_stats["n_vars"])
        )
    # transfer protein_expression
    protein_expression_obsm_key = _transfer_protein_expression(_scvi_dict, adata_target)

    # transfer batch and labels
    categorical_mappings = _scvi_dict["categorical_mappings"]
    for key, val in categorical_mappings.items():
        original_key = val["original_key"]
        if (key == original_key) and (original_key not in adata_target.obs.keys()):
            # case where original key and key are equal
            # caused when no batch or label key were given
            # when anndata_source was setup
            logger.info(
                ".obs[{}] not found in target, assuming every cell is same category".format(
                    original_key
                )
            )
            adata_target.obs[original_key] = np.zeros(
                adata_target.shape[0], dtype=np.int64
            )
        elif (key != original_key) and (original_key not in adata_target.obs.keys()):
            raise KeyError(
                '.obs["{}"] was used to setup source, but not found in target.'.format(
                    original_key
                )
            )
        mapping = val["mapping"]
        cat_dtype = CategoricalDtype(categories=mapping)
        _make_obs_column_categorical(
            adata_target, original_key, key, categorical_dtype=cat_dtype
        )

    batch_key = "_scvi_batch"
    labels_key = "_scvi_labels"

    # transfer X
    x_loc, x_key = _setup_x(adata_target, layer, use_raw)
    local_l_mean_key, local_l_var_key = _setup_library_size(
        adata_target, batch_key, layer, use_raw
    )
    target_data_registry = data_registry.copy()
    target_data_registry.update(
        {_CONSTANTS.X_KEY: {"attr_name": x_loc, "attr_key": x_key}}
    )
    # transfer extra categorical covs
    has_cat_cov = True if _CONSTANTS.CAT_COVS_KEY in data_registry.keys() else False
    if has_cat_cov:
        source_cat_dict = _scvi_dict["extra_categorical_mappings"]
        cat_loc, cat_key = _setup_extra_categorical_covs(
            adata_target, list(source_cat_dict.keys()), category_dict=source_cat_dict
        )
        target_data_registry.update(
            {_CONSTANTS.CAT_COVS_KEY: {"attr_name": cat_loc, "attr_key": cat_key}}
        )
    else:
        source_cat_dict = None

    # transfer extra continuous covs
    has_cont_cov = True if _CONSTANTS.CONT_COVS_KEY in data_registry.keys() else False
    if has_cont_cov:
        obs_keys_names = _scvi_dict["extra_continuous_keys"]
        cont_loc, cont_key = _setup_extra_continuous_covs(
            adata_target, list(obs_keys_names)
        )
        target_data_registry.update(
            {_CONSTANTS.CONT_COVS_KEY: {"attr_name": cont_loc, "attr_key": cont_key}}
        )
    else:
        obs_keys_names = None

    # add the data_registry to anndata
    _register_anndata(adata_target, data_registry_dict=target_data_registry)
    logger.info("Registered keys:{}".format(list(target_data_registry.keys())))
    _setup_summary_stats(
        adata_target,
        batch_key,
        labels_key,
        protein_expression_obsm_key,
        source_cat_dict,
        obs_keys_names,
    )
    _verify_and_correct_data_format(adata_target, data_registry)