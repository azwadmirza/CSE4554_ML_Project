def get_array_index_type(ary, idx):
    """
    Returns None or a tuple-3 for the types of the input array, index, and
    resulting type of ``array[index]``.

    Note: This is shared logic for ndarray getitem and setitem.
    """
    if not isinstance(ary, types.Buffer):
        return

    ndim = ary.ndim

    left_indices = []
    right_indices = []
    ellipsis_met = False
    advanced = False
    has_integer = False

    if not isinstance(idx, types.BaseTuple):
        idx = [idx]

    # Walk indices
    for ty in idx:
        if ty is types.ellipsis:
            if ellipsis_met:
                raise TypeError("only one ellipsis allowed in array index "
                                "(got %s)" % (idx,))
            ellipsis_met = True
        elif isinstance(ty, types.SliceType):
            pass
        elif isinstance(ty, types.Integer):
            # Normalize integer index
            ty = types.intp if ty.signed else types.uintp
            # Integer indexing removes the given dimension
            ndim -= 1
            has_integer = True
        elif (isinstance(ty, types.Array) and ty.ndim == 0
              and isinstance(ty.dtype, types.Integer)):
            # 0-d array used as integer index
            ndim -= 1
            has_integer = True
        elif (isinstance(ty, types.Array)
              and ty.ndim == 1
              and isinstance(ty.dtype, (types.Integer, types.Boolean))):
            if advanced or has_integer:
                # We don't support the complicated combination of
                # advanced indices (and integers are considered part
                # of them by Numpy).
                raise NotImplementedError("only one advanced index supported")
            advanced = True
        else:
            raise TypeError("unsupported array index type %s in %s"
                            % (ty, idx))
        (right_indices if ellipsis_met else left_indices).append(ty)

    # Only Numpy arrays support advanced indexing
    if advanced and not isinstance(ary, types.Array):
        return

    # Check indices and result dimensionality
    all_indices = left_indices + right_indices
    if ellipsis_met:
        assert right_indices[0] is types.ellipsis
        del right_indices[0]

    n_indices = len(all_indices) - ellipsis_met
    if n_indices > ary.ndim:
        raise TypeError("cannot index %s with %d indices: %s"
                        % (ary, n_indices, idx))
    if n_indices == ary.ndim and ndim == 0 and not ellipsis_met:
        # Full integer indexing => scalar result
        # (note if ellipsis is present, a 0-d view is returned instead)
        res = ary.dtype

    elif advanced:
        # Result is a copy
        res = ary.copy(ndim=ndim, layout='C', readonly=False)

    else:
        # Result is a view
        if ary.slice_is_copy:
            # Avoid view semantics when the original type creates a copy
            # when slicing.
            return

        # Infer layout
        layout = ary.layout

        def keeps_contiguity(ty, is_innermost):
            # A slice can only keep an array contiguous if it is the
            # innermost index and it is not strided
            return (ty is types.ellipsis or isinstance(ty, types.Integer)
                    or (is_innermost and isinstance(ty, types.SliceType)
                        and not ty.has_step))

        def check_contiguity(outer_indices):
            """
            Whether indexing with the given indices (from outer to inner in
            physical layout order) can keep an array contiguous.
            """
            for ty in outer_indices[:-1]:
                if not keeps_contiguity(ty, False):
                    return False
            if outer_indices and not keeps_contiguity(outer_indices[-1], True):
                return False
            return True

        if layout == 'C':
            # Integer indexing on the left keeps the array C-contiguous
            if n_indices == ary.ndim:
                # If all indices are there, ellipsis's place is indifferent
                left_indices = left_indices + right_indices
                right_indices = []
            if right_indices:
                layout = 'A'
            elif not check_contiguity(left_indices):
                layout = 'A'
        elif layout == 'F':
            # Integer indexing on the right keeps the array F-contiguous
            if n_indices == ary.ndim:
                # If all indices are there, ellipsis's place is indifferent
                right_indices = left_indices + right_indices
                left_indices = []
            if left_indices:
                layout = 'A'
            elif not check_contiguity(right_indices[::-1]):
                layout = 'A'

        if ndim == 0:
            # Implicitly convert to a scalar if the output ndim==0
            res = ary.dtype
        else:
            res = ary.copy(ndim=ndim, layout=layout)

    # Re-wrap indices
    if isinstance(idx, types.BaseTuple):
        idx = types.BaseTuple.from_types(all_indices)
    else:
        idx, = all_indices

    return Indexing(idx, res, advanced)