def create_target_index(lang):
    return create_in(
        appsettings.WHOOSH_INDEX,
        schema=TARGET_SCHEMA,
        indexname='target-%s' % lang
    )