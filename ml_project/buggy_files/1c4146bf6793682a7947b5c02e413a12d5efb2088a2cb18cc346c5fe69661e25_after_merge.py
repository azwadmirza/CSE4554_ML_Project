def convert_label_indexer(index, label, index_name='', method=None,
                          tolerance=None):
    """Given a pandas.Index and labels (e.g., from __getitem__) for one
    dimension, return an indexer suitable for indexing an ndarray along that
    dimension. If `index` is a pandas.MultiIndex and depending on `label`,
    return a new pandas.Index or pandas.MultiIndex (otherwise return None).
    """
    new_index = None

    if isinstance(label, slice):
        if method is not None or tolerance is not None:
            raise NotImplementedError(
                'cannot use ``method`` argument if any indexers are '
                'slice objects')
        indexer = index.slice_indexer(_sanitize_slice_element(label.start),
                                      _sanitize_slice_element(label.stop),
                                      _sanitize_slice_element(label.step))
        if not isinstance(indexer, slice):
            # unlike pandas, in xarray we never want to silently convert a
            # slice indexer into an array indexer
            raise KeyError('cannot represent labeled-based slice indexer for '
                           'dimension %r with a slice over integer positions; '
                           'the index is unsorted or non-unique' % index_name)

    elif is_dict_like(label):
        is_nested_vals = _is_nested_tuple(tuple(label.values()))
        if not isinstance(index, pd.MultiIndex):
            raise ValueError('cannot use a dict-like object for selection on '
                             'a dimension that does not have a MultiIndex')
        elif len(label) == index.nlevels and not is_nested_vals:
            indexer = index.get_loc(tuple((label[k] for k in index.names)))
        else:
            for k, v in label.items():
                # index should be an item (i.e. Hashable) not an array-like
                if not isinstance(v, Hashable):
                    raise ValueError('Vectorized selection is not '
                                     'available along level variable: ' + k)
            indexer, new_index = index.get_loc_level(
                tuple(label.values()), level=tuple(label.keys()))

    elif isinstance(label, tuple) and isinstance(index, pd.MultiIndex):
        if _is_nested_tuple(label):
            indexer = index.get_locs(label)
        elif len(label) == index.nlevels:
            indexer = index.get_loc(label)
        else:
            indexer, new_index = index.get_loc_level(
                label, level=list(range(len(label)))
            )

    else:
        label = (label if getattr(label, 'ndim', 1) > 1  # vectorized-indexing
                 else _asarray_tuplesafe(label))
        if label.ndim == 0:
            if isinstance(index, pd.MultiIndex):
                indexer, new_index = index.get_loc_level(label.item(), level=0)
            else:
                indexer = get_loc(index, label.item(), method, tolerance)
        elif label.dtype.kind == 'b':
            indexer = label
        else:
            if isinstance(index, pd.MultiIndex) and label.ndim > 1:
                raise ValueError('Vectorized selection is not available along '
                                 'MultiIndex variable: ' + index_name)
            indexer = get_indexer_nd(index, label, method, tolerance)
            if np.any(indexer < 0):
                raise KeyError('not all values found in index %r'
                               % index_name)
    return indexer, new_index