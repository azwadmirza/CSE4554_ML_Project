def _notify_deleted_relationships(session, obj):
    """Expire relationships when an object becomes deleted

    Needed for
    """
    mapper = inspect(obj).mapper
    for prop in mapper.relationships:
        if prop.back_populates:
            _expire_relationship(obj, prop)