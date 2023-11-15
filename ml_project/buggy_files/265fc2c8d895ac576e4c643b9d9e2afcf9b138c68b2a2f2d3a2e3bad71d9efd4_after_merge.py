def get_index_trap(*args, **kwargs):
    """
    Retrieves the package index, but traps exceptions and reports them as
    JSON if necessary.
    """
    from ..core.index import get_index
    kwargs.pop('json', None)
    return get_index(*args, **kwargs)