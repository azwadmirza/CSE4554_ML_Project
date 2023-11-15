def _make_indexable(iterable):
    """Ensure iterable supports indexing or convert to an indexable variant.

    Convert sparse matrices to csr and other non-indexable iterable to arrays.
    Let `None` and indexable objects (e.g. pandas dataframes) pass unchanged.

    Parameters
    ----------
    iterable : {list, dataframe, array, sparse} or None
        Object to be converted to an indexable iterable.
    """
    if issparse(iterable):
        return mt.tensor(iterable)
    elif hasattr(iterable, "iloc"):
        return md.DataFrame(iterable)
    elif hasattr(iterable, "__getitem__"):
        return mt.tensor(iterable)
    elif iterable is None:
        return iterable
    return mt.tensor(iterable)