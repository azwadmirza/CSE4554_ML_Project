def type_of_target(y):
    """Determine the type of data indicated by the target.

    Note that this type is the most specific type that can be inferred.
    For example:

        * ``binary`` is more specific but compatible with ``multiclass``.
        * ``multiclass`` of integers is more specific but compatible with
          ``continuous``.
        * ``multilabel-indicator`` is more specific but compatible with
          ``multiclass-multioutput``.

    Parameters
    ----------
    y : array-like

    Returns
    -------
    target_type : string
        One of:

        * 'continuous': `y` is an array-like of floats that are not all
          integers, and is 1d or a column vector.
        * 'continuous-multioutput': `y` is a 2d tensor of floats that are
          not all integers, and both dimensions are of size > 1.
        * 'binary': `y` contains <= 2 discrete values and is 1d or a column
          vector.
        * 'multiclass': `y` contains more than two discrete values, is not a
          sequence of sequences, and is 1d or a column vector.
        * 'multiclass-multioutput': `y` is a 2d tensor that contains more
          than two discrete values, is not a sequence of sequences, and both
          dimensions are of size > 1.
        * 'multilabel-indicator': `y` is a label indicator matrix, a tensor
          of two dimensions with at least two columns, and at most 2 unique
          values.
        * 'unknown': `y` is array-like but none of the above, such as a 3d
          tensor, sequence of sequences, or a tensor of non-sequence objects.

    Examples
    --------
    >>> import mars.tensor as mt
    >>> from mars.learn.utils.multiclass import type_of_target
    >>> type_of_target([0.1, 0.6]).execute()
    'continuous'
    >>> type_of_target([1, -1, -1, 1]).execute()
    'binary'
    >>> type_of_target(['a', 'b', 'a']).execute()
    'binary'
    >>> type_of_target([1.0, 2.0]).execute()
    'binary'
    >>> type_of_target([1, 0, 2]).execute()
    'multiclass'
    >>> type_of_target([1.0, 0.0, 3.0]).execute()
    'multiclass'
    >>> type_of_target(['a', 'b', 'c']).execute()
    'multiclass'
    >>> type_of_target(mt.array([[1, 2], [3, 1]])).execute()
    'multiclass-multioutput'
    >>> type_of_target([[1, 2]]).execute()
    'multiclass-multioutput'
    >>> type_of_target(mt.array([[1.5, 2.0], [3.0, 1.6]])).execute()
    'continuous-multioutput'
    >>> type_of_target(mt.array([[0, 1], [1, 1]])).execute()
    'multilabel-indicator'
    """
    valid_types = (Sequence, spmatrix) if spmatrix is not None else (Sequence,)
    valid = ((isinstance(y, valid_types) or
              hasattr(y, '__array__') or hasattr(y, '__mars_tensor__'))
             and not isinstance(y, str))

    if not valid:
        raise ValueError(f'Expected array-like (array or non-string sequence), got {y}')

    sparse_pandas = (y.__class__.__name__ in ['SparseSeries', 'SparseArray'])
    if sparse_pandas:  # pragma: no cover
        raise ValueError("y cannot be class 'SparseSeries' or 'SparseArray'")

    if isinstance(y, (Base, Entity)):
        y = mt.tensor(y)

    op = TypeOfTarget(y=y)
    return op(y)