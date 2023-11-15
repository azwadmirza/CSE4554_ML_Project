def ensure_sequence_of_iterables(obj, length: Optional[int] = None):
    """Ensure that ``obj`` behaves like a (nested) sequence of iterables.

    If length is provided and the object is already a sequence of iterables,
    a ValueError will be raised if ``len(obj) != length``.

    Parameters
    ----------
    obj : Any
        the object to check
    length : int, optional
        If provided, assert that obj has len ``length``, by default None

    Returns
    -------
    iterable
        nested sequence of iterables, or an itertools.repeat instance

    Examples
    --------
    In [1]: ensure_sequence_of_iterables([1, 2])
    Out[1]: repeat([1, 2])

    In [2]: ensure_sequence_of_iterables([(1, 2), (3, 4)])
    Out[2]: [(1, 2), (3, 4)]

    In [3]: ensure_sequence_of_iterables({'a':1})
    Out[3]: repeat({'a': 1})

    In [4]: ensure_sequence_of_iterables(None)
    Out[4]: repeat(None)
    """

    if obj is not None and is_sequence(obj) and is_iterable(obj[0]):
        if length is not None and len(obj) != length:
            raise ValueError(f"length of {obj} must equal {length}")
        return obj
    return itertools.repeat(obj)