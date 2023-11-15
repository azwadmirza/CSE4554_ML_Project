def dataset_update_method(dataset, other):
    """Guts of the Dataset.update method"""
    objs = [dataset, other]
    priority_arg = 1
    indexes = dataset.indexes
    return merge_core(objs, priority_arg=priority_arg, indexes=indexes)