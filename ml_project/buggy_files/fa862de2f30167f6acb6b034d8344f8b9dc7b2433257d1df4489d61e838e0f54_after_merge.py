def dataset_update_method(dataset, other):
    """Guts of the Dataset.update method"""
    return merge_core([dataset, other], priority_arg=1, indexes=dataset.indexes,
                      indexes_from_arg=0)