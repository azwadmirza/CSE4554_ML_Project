def create_from_config(config, prefix=''):
    """Create a PostgreSQLClient client using settings in the provided config.
    """
    if sqlalchemy is None:
        message = ("PostgreSQL dependencies missing. "
                   "Refer to installation section in documentation.")
        raise ImportWarning(message)

    settings = config.get_settings()
    url = settings[prefix + 'url']

    if url in _ENGINES:
        msg = ("Reuse existing PostgreSQL connection. "
               "Parameters %s* will be ignored." % prefix)
        warnings.warn(msg)
        return PostgreSQLClient(_ENGINES[url])

    # Initialize SQLAlchemy engine.
    poolclass_key = prefix + 'poolclass'
    settings.setdefault(poolclass_key, 'sqlalchemy.pool.QueuePool')
    settings[poolclass_key] = config.maybe_dotted(settings[poolclass_key])
    settings.pop(prefix + 'max_fetch_size', None)
    settings.pop(prefix + 'backend', None)

    # XXX: Disable pooling at least during tests to avoid stalled tests.
    if os.getenv('TRAVIS', False):  # pragma: no cover
        warnings.warn('Disable pooling on TravisCI')
        settings = dict([(poolclass_key, sqlalchemy.pool.StaticPool)])

    engine = sqlalchemy.engine_from_config(settings, prefix=prefix, url=url)

    # Store one engine per URI.
    _ENGINES[url] = engine

    return PostgreSQLClient(engine)