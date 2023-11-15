def with_row_locks(query, **kwargs):
    """
    Apply with_for_update to an SQLAlchemy query, if row level locking is in use.

    :param query: An SQLAlchemy Query object
    :param kwargs: Extra kwargs to pass to with_for_update (of, nowait, skip_locked, etc)
    :return: updated query
    """
    if USE_ROW_LEVEL_LOCKING:
        return query.with_for_update(**kwargs)
    else:
        return query