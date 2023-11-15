    def __init__(self, servers=None, keyspace=None, table=None, entry_ttl=None,
                 port=9042, **kwargs):
        super(CassandraBackend, self).__init__(**kwargs)

        if not cassandra:
            raise ImproperlyConfigured(E_NO_CASSANDRA)

        conf = self.app.conf
        self.servers = servers or conf.get('cassandra_servers', None)
        self.port = port or conf.get('cassandra_port', None)
        self.keyspace = keyspace or conf.get('cassandra_keyspace', None)
        self.table = table or conf.get('cassandra_table', None)
        self.cassandra_options = conf.get('cassandra_options', {})

        if not self.servers or not self.keyspace or not self.table:
            raise ImproperlyConfigured('Cassandra backend not configured.')

        expires = entry_ttl or conf.get('cassandra_entry_ttl', None)

        self.cqlexpires = (
            Q_EXPIRES.format(expires) if expires is not None else '')

        read_cons = conf.get('cassandra_read_consistency') or 'LOCAL_QUORUM'
        write_cons = conf.get('cassandra_write_consistency') or 'LOCAL_QUORUM'

        self.read_consistency = getattr(
            cassandra.ConsistencyLevel, read_cons,
            cassandra.ConsistencyLevel.LOCAL_QUORUM)
        self.write_consistency = getattr(
            cassandra.ConsistencyLevel, write_cons,
            cassandra.ConsistencyLevel.LOCAL_QUORUM)

        self.auth_provider = None
        auth_provider = conf.get('cassandra_auth_provider', None)
        auth_kwargs = conf.get('cassandra_auth_kwargs', None)
        if auth_provider and auth_kwargs:
            auth_provider_class = getattr(cassandra.auth, auth_provider, None)
            if not auth_provider_class:
                raise ImproperlyConfigured(E_NO_SUCH_CASSANDRA_AUTH_PROVIDER)
            self.auth_provider = auth_provider_class(**auth_kwargs)

        self._connection = None
        self._session = None
        self._write_stmt = None
        self._read_stmt = None
        self._make_stmt = None