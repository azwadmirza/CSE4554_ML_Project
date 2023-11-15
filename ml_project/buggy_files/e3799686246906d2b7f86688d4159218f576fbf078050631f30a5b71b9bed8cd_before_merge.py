def _get_batch_code_from_category(
    adata: anndata.AnnData, category: Sequence[Union[int, str]]
):
    categorical_mappings = adata.uns["_scvi"]["categorical_mappings"]
    batch_mappings = categorical_mappings["_scvi_batch"]["mapping"]
    batch_code = []
    for cat in category:
        if cat is None:
            batch_code.append(None)
        elif cat not in batch_mappings:
            raise ValueError('"{}" not a valid batch category.'.format(cat))
        else:
            batch_loc = np.where(batch_mappings == cat)[0][0]
            batch_code.append(batch_loc)
    return batch_code