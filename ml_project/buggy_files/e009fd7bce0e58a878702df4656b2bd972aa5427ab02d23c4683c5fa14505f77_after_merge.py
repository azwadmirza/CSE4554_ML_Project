def _non_reducing_slice(slice_):
    """
    Ensurse that a slice doesn't reduce to a Series or Scalar.

    Any user-paseed `subset` should have this called on it
    to make sure we're always working with DataFrames.
    """
    # default to column slice, like DataFrame
    # ['A', 'B'] -> IndexSlices[:, ['A', 'B']]
    kinds = tuple(list(compat.string_types) + [ABCSeries, np.ndarray, Index,
                                               list])
    if isinstance(slice_, kinds):
        slice_ = IndexSlice[:, slice_]

    def pred(part):
        # true when slice does *not* reduce, False when part is a tuple,
        # i.e. MultiIndex slice
        return ((isinstance(part, slice) or is_list_like(part))
                and not isinstance(part, tuple))

    if not is_list_like(slice_):
        if not isinstance(slice_, slice):
            # a 1-d slice, like df.loc[1]
            slice_ = [[slice_]]
        else:
            # slice(a, b, c)
            slice_ = [slice_]  # to tuplize later
    else:
        slice_ = [part if pred(part) else [part] for part in slice_]
    return tuple(slice_)