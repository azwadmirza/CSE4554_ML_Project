def partial_align(*objects, **kwargs):
    """partial_align(*objects, join='inner', copy=True, indexes=None,
                     exclude=set())

    Like align, but don't align along dimensions in exclude. Any indexes
    explicitly provided with the `indexes` argument should be used in preference
    to the aligned indexes.

    Not public API.
    """
    join = kwargs.pop('join', 'inner')
    copy = kwargs.pop('copy', True)
    indexes = kwargs.pop('indexes', None)
    exclude = kwargs.pop('exclude', None)
    if exclude is None:
        exclude = set()
    if kwargs:
        raise TypeError('align() got unexpected keyword arguments: %s'
                        % list(kwargs))

    joined_indexes = _join_indexes(join, objects, exclude=exclude)
    if indexes is not None:
        joined_indexes.update(indexes)

    result = []
    for obj in objects:
        valid_indexers = dict((k, v) for k, v in joined_indexes.items()
                              if k in obj.dims)
        result.append(obj.reindex(copy=copy, **valid_indexers))

    return tuple(result)