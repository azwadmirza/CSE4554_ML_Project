def _setup_summary_stats(
    adata,
    batch_key,
    labels_key,
    protein_expression_obsm_key,
    categorical_covariate_keys,
    continuous_covariate_keys,
):
    categorical_mappings = adata.uns["_scvi"]["categorical_mappings"]
    use_raw = adata.uns["_scvi"]["use_raw"]

    n_batch = len(np.unique(categorical_mappings[batch_key]["mapping"]))
    n_cells = adata.shape[0]
    n_vars = adata.shape[1] if not use_raw else adata.raw.shape[1]
    n_labels = len(np.unique(categorical_mappings[labels_key]["mapping"]))

    if protein_expression_obsm_key is not None:
        n_proteins = adata.obsm[protein_expression_obsm_key].shape[1]
    else:
        n_proteins = 0

    if categorical_covariate_keys is not None:
        n_cat_covs = len(categorical_covariate_keys)
    else:
        n_cat_covs = 0

    if continuous_covariate_keys is not None:
        n_cont_covs = len(continuous_covariate_keys)
    else:
        n_cont_covs = 0

    summary_stats = {
        "n_batch": n_batch,
        "n_cells": n_cells,
        "n_vars": n_vars,
        "n_labels": n_labels,
        "n_proteins": n_proteins,
    }
    adata.uns["_scvi"]["summary_stats"] = summary_stats
    logger.info(
        "Successfully registered anndata object containing {} cells, {} vars, "
        "{} batches, {} labels, and {} proteins. Also registered {} extra categorical "
        "covariates and {} extra continuous covariates.".format(
            n_cells, n_vars, n_batch, n_labels, n_proteins, n_cat_covs, n_cont_covs
        )
    )

    return summary_stats