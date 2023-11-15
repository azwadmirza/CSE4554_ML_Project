def _normalize_dataframe(dataframe, index):
    """Take a pandas DataFrame and count the element present in the
    given columns, return a hierarchical index on those columns
    """
    #groupby the given keys, extract the same columns and count the element
    # then collapse them with a mean
    data = dataframe[index].dropna()
    grouped = data.groupby(index, sort=False)
    counted = grouped[index].count()
    averaged = counted.mean(axis=1)
    return averaged