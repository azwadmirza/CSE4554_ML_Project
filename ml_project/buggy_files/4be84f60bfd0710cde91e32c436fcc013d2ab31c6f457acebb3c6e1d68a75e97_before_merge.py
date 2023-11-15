def unique_with_labels(values):
    uniques = Index(lib.fast_unique(values))
    labels = lib.get_unique_labels(values, uniques.indexMap)
    return uniques, labels