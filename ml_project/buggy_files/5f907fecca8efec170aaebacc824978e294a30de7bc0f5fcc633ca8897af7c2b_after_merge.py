def with_row_locks(query, session: Session, **kwargs):
    """
    Apply with_for_update to an SQLAlchemy query, if row level locking is in use.

    :param query: An SQLAlchemy Query object
    :param session: ORM Session
    :param kwargs: Extra kwargs to pass to with_for_update (of, nowait, skip_locked, etc)
    :return: updated query
    """
    dialect = session.bind.dialect

    # Don't use row level locks if the MySQL dialect (Mariadb & MySQL < 8) does not support it.
    if USE_ROW_LEVEL_LOCKING and (dialect.name != "mysql" or dialect.supports_for_update_of):
        return query.with_for_update(**kwargs)
    else:
        return query