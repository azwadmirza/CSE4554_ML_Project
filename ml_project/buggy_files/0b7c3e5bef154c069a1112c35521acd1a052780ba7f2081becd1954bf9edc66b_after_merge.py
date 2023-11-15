def unique1d(values):
    """
    Hash table-based unique
    """
    if np.issubdtype(values.dtype, np.floating):
        table = lib.Float64HashTable(len(values))
        uniques = np.array(table.unique(com._ensure_float64(values)),
                           dtype=np.float64)
    elif np.issubdtype(values.dtype, np.datetime64):
        table = lib.Int64HashTable(len(values))
        uniques = np.array(table.unique(com._ensure_int64(values)),
                           dtype=np.int64)
        uniques = uniques.view('M8[ns]')
    elif np.issubdtype(values.dtype, np.integer):
        table = lib.Int64HashTable(len(values))
        uniques = np.array(table.unique(com._ensure_int64(values)),
                           dtype=np.int64)
    else:
        table = lib.PyObjectHashTable(len(values))
        uniques = table.unique(com._ensure_object(values))
        uniques = lib.list_to_object_array(uniques)
    return uniques