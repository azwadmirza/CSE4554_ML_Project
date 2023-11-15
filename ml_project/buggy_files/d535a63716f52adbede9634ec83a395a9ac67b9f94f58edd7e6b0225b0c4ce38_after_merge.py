def _get_var_names_from_setup_anndata(adata):
    """Gets var names by checking if using raw."""
    var_names = adata.var_names
    return var_names