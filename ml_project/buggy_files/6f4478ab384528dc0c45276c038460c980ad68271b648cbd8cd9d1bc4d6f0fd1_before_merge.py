def _set_data_in_registry(adata, data, key):
    """
    Sets the data associated with key in adata.uns['_scvi']['data_registry'].keys() to data.

    Note: This is a dangerous method and will change the underlying data of the user's anndata
    Currently used to make the user's anndata C_CONTIGUOUS and csr if it is dense numpy
    or sparse respectively.

    Parameters
    ----------
    adata
        anndata object to change data of
    data
        data to change to
    key
        key in adata.uns['_scvi]['data_registry'].keys() associated with the data
    """
    use_raw = adata.uns["_scvi"]["use_raw"]
    data_loc = adata.uns["_scvi"]["data_registry"][key]
    attr_name, attr_key = data_loc["attr_name"], data_loc["attr_key"]

    if use_raw is True and attr_name in ["X", "var"]:
        tmp_adata = adata.raw.to_adata()
    else:
        tmp_adata = adata
    if attr_key == "None":
        setattr(tmp_adata, attr_name, data)

    elif attr_key != "None":
        attribute = getattr(tmp_adata, attr_name)
        if isinstance(attribute, pd.DataFrame):
            attribute.loc[:, attr_key] = data
        else:
            attribute[attr_key] = data
        setattr(tmp_adata, attr_name, attribute)

    if use_raw is True and attr_name in ["X", "var"]:
        adata.raw = tmp_adata