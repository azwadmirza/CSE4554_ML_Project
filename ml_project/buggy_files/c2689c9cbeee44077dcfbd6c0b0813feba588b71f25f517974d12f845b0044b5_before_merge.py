def _setup_library_size(adata, batch_key, layer, use_raw):
    # computes the library size per batch
    logger.info("Computing library size prior per batch")
    local_l_mean_key = "_scvi_local_l_mean"
    local_l_var_key = "_scvi_local_l_var"
    _compute_library_size_batch(
        adata,
        batch_key=batch_key,
        local_l_mean_key=local_l_mean_key,
        local_l_var_key=local_l_var_key,
        layer=layer,
        use_raw=use_raw,
    )
    return local_l_mean_key, local_l_var_key