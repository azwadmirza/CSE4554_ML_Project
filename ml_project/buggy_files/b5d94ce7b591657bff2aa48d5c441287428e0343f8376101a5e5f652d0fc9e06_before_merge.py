def create_target_index(lang):
    return create_in(
        settings.WHOOSH_INDEX,
        schema=TARGET_SCHEMA,
        indexname='target-%s' % lang
    )