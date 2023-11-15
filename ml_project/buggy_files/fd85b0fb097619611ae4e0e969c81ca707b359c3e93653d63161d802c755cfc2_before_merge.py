def _check_anndata_setup_equivalence(adata_source, adata_target):
    """Checks if target setup is equivalent to source."""
    if isinstance(adata_source, anndata.AnnData):
        _scvi_dict = adata_source.uns["_scvi"]
    else:
        _scvi_dict = adata_source
    adata = adata_target

    stats = _scvi_dict["summary_stats"]
    use_raw = _scvi_dict["use_raw"]

    target_n_vars = adata.shape[1] if not use_raw else adata.raw.shape[1]
    error_msg = (
        "Number of {} in anndata different from initial anndata used for training."
    )
    if target_n_vars != stats["n_genes"]:
        raise ValueError(error_msg.format("genes"))

    error_msg = (
        "There are more {} categories in the data than were originally registered. "
        + "Please check your {} categories as well as adata.uns['_scvi']['categorical_mappings']."
    )
    self_categoricals = _scvi_dict["categorical_mappings"]
    self_batch_mapping = self_categoricals["_scvi_batch"]["mapping"]

    adata_categoricals = adata.uns["_scvi"]["categorical_mappings"]
    adata_batch_mapping = adata_categoricals["_scvi_batch"]["mapping"]
    # check if the categories are the same
    error_msg = (
        "Categorial encoding for {} is not the same between "
        + "the anndata used to train the model and the anndata just passed in. "
        + "Categorical encoding needs to be same elements, same order, and same datatype.\n"
        + "Expected categories: {}. Received categories: {}.\n"
        + "Try running `dataset.transfer_anndata_setup()` or deleting `adata.uns['_scvi']."
    )
    if np.sum(self_batch_mapping == adata_batch_mapping) != len(self_batch_mapping):
        raise ValueError(
            error_msg.format("batch", self_batch_mapping, adata_batch_mapping)
        )
    self_labels_mapping = self_categoricals["_scvi_labels"]["mapping"]
    adata_labels_mapping = adata_categoricals["_scvi_labels"]["mapping"]
    if np.sum(self_labels_mapping == adata_labels_mapping) != len(self_labels_mapping):
        raise ValueError(
            error_msg.format("label", self_labels_mapping, adata_labels_mapping)
        )

    # validate any extra categoricals
    if "extra_categorical_mappings" in _scvi_dict.keys():
        target_extra_cat_maps = adata.uns["_scvi"]["extra_categorical_mappings"]
        for key, val in _scvi_dict["extra_categorical_mappings"].items():
            target_map = target_extra_cat_maps[key]
            if np.sum(val == target_map) != len(val):
                raise ValueError(error_msg.format(key, val, target_map))
    # validate any extra continuous covs
    if "extra_continuous_keys" in _scvi_dict.keys():
        if "extra_continuous_keys" not in adata.uns["_scvi"].keys():
            raise ValueError('extra_continuous_keys not in adata.uns["_scvi"]')
        target_cont_keys = adata.uns["_scvi"]["extra_continuous_keys"]
        if not _scvi_dict["extra_continuous_keys"].equals(target_cont_keys):
            raise ValueError(
                "extra_continous_keys are not the same between source and target"
            )