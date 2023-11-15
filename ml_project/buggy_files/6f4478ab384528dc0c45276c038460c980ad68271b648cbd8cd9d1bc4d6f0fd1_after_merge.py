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
    data_loc = adata.uns["_scvi"]["data_registry"][key]
    attr_name, attr_key = data_loc["attr_name"], data_loc["attr_key"]

    if attr_key == "None":
        setattr(adata, attr_name, data)

    elif attr_key != "None":
        attribute = getattr(adata, attr_name)
        if isinstance(attribute, pd.DataFrame):
            attribute.loc[:, attr_key] = data
        else:
            attribute[attr_key] = data
        setattr(adata, attr_name, attribute)