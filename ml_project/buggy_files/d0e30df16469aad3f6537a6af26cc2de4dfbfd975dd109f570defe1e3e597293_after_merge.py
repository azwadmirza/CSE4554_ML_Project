def create_source_index():
    return create_in(
        appsettings.WHOOSH_INDEX,
        schema=SOURCE_SCHEMA,
        indexname='source'
    )