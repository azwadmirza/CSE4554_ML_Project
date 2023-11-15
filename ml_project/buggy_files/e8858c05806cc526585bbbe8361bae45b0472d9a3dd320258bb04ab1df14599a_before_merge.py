def type_of_target(y):
    """Determine the type of data indicated by target `y`

    Parameters
    ----------
    y : array-like

    Returns
    -------
    target_type : string
        One of:
        * 'continuous': `y` is an array-like of floats that are not all
          integers, and is 1d or a column vector.
        * 'continuous-multioutput': `y` is a 2d array of floats that are
          not all integers, and both dimensions are of size > 1.
        * 'binary': `y` contains <= 2 discrete values and is 1d or a column
          vector.
        * 'multiclass': `y` contains more than two discrete values, is not a
          sequence of sequences, and is 1d or a column vector.
        * 'mutliclass-multioutput': `y` is a 2d array that contains more
          than two discrete values, is not a sequence of sequences, and both
          dimensions are of size > 1.
        * 'multilabel-sequences': `y` is a sequence of sequences, a 1d
          array-like of objects that are sequences of labels.
        * 'multilabel-indicator': `y` is a label indicator matrix, an array
          of two dimensions with at least two columns, and at most 2 unique
          values.
        * 'unknown': `y` is array-like but none of the above, such as a 3d
          array, or an array of non-sequence objects.

    Examples
    --------
    >>> import numpy as np
    >>> type_of_target([0.1, 0.6])
    'continuous'
    >>> type_of_target([1, -1, -1, 1])
    'binary'
    >>> type_of_target(['a', 'b', 'a'])
    'binary'
    >>> type_of_target([1, 0, 2])
    'multiclass'
    >>> type_of_target(['a', 'b', 'c'])
    'multiclass'
    >>> type_of_target(np.array([[1, 2], [3, 1]]))
    'multiclass-multioutput'
    >>> type_of_target(np.array([[1.5, 2.0], [3.0, 1.6]]))
    'continuous-multioutput'
    >>> type_of_target(np.array([[0, 1], [1, 1]]))
    'multilabel-indicator'
    """
    # XXX: is there a way to duck-type this condition?
    valid = (isinstance(y, (np.ndarray, Sequence))
             and not isinstance(y, string_types))
    if not valid:
        raise ValueError('Expected array-like (array or non-string sequence), '
                         'got %r' % y)

    if is_sequence_of_sequences(y):
        return 'multilabel-sequences'
    elif is_label_indicator_matrix(y):
        return 'multilabel-indicator'

    try:
        y = np.asarray(y)
    except ValueError:
        # known to fail in numpy 1.3 for array of arrays
        return 'unknown'
    if y.ndim > 2 or (y.dtype == object and len(y) and
                      not isinstance(y.flat[0], string_types)):
        return 'unknown'
    if y.ndim == 2 and y.shape[1] == 0:
        return 'unknown'
    elif y.ndim == 2 and y.shape[1] > 1:
        suffix = '-multioutput'
    else:
        # column vector or 1d
        suffix = ''

    # check float and contains non-integer float values:
    if y.dtype.kind == 'f' and np.any(y != y.astype(int)):
        return 'continuous' + suffix
    if len(np.unique(y)) <= 2:
        assert not suffix, "2d binary array-like should be multilabel"
        return 'binary'
    else:
        return 'multiclass' + suffix