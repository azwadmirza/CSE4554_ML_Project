    def __init__(self, host='127.0.0.1', port=9200):
        """Create a Elasticsearch client."""
        super().__init__()
        self._error_container = {}

        self.user = current_app.config.get('ELASTIC_USER', 'user')
        self.password = current_app.config.get('ELASTIC_PASSWORD', 'pass')
        self.ssl = current_app.config.get('ELASTIC_SSL', False)
        self.verify = current_app.config.get('ELASTIC_VERIFY_CERTS', True)

        if self.ssl:
            self.client = Elasticsearch([{'host': host, 'port': port}],
                                        http_auth=(self.user, self.password),
                                        use_ssl=self.ssl,
                                        verify_certs=self.verify)
        else:
            self.client = Elasticsearch([{'host': host, 'port': port}])

        self.import_counter = Counter()
        self.import_events = []
        self._request_timeout = current_app.config.get(
            'TIMEOUT_FOR_EVENT_IMPORT', self.DEFAULT_EVENT_IMPORT_TIMEOUT)