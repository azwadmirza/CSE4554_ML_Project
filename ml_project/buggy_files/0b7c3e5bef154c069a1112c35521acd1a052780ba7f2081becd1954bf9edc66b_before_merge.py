def unique1d(values):
    """
    Hash table-based unique
    """
    if issubclass(values.dtype.type, np.floating):
        if values.dtype != np.float64:
            values = values.astype(np.float64)
        table = lib.Float64HashTable(len(values))
        uniques = np.array(table.unique(values), dtype=np.float64)
    elif issubclass(values.dtype.type, np.integer):
        if values.dtype != np.int64:
            values = values.astype(np.int64)
        table = lib.Int64HashTable(len(values))
        uniques = np.array(table.unique(values), dtype=np.int64)
    else:
        if not values.dtype == np.object_:
            values = values.astype(np.object_)
        table = lib.PyObjectHashTable(len(values))
        uniques = lib.list_to_object_array(table.unique(values))
    return uniques