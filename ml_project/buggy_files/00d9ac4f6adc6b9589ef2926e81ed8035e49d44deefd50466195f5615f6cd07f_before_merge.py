    def init(self):
        if Elasticsearch is None:
            raise MissingDependencyError('elasticsearch', version='>=5.0.0,<6.0.0')

        self.elastic_host = getattr(self.parameters,
                                    'elastic_host', '127.0.0.1')
        self.elastic_port = getattr(self.parameters,
                                    'elastic_port', '9200')
        self.elastic_index = getattr(self.parameters,
                                     'elastic_index', 'intelmq')
        self.rotate_index = getattr(self.parameters,
                                    'rotate_index', False)
        self.use_ssl = getattr(self.parameters,
                               'use_ssl', False)
        self.ssl_ca_certificate = getattr(self.parameters,
                                          'ssl_ca_certificate', None)
        self.ssl_show_warnings = getattr(self.parameters,
                                         'ssl_show_warnings', True)
        self.elastic_doctype = getattr(self.parameters,
                                       'elastic_doctype', 'events')
        self.replacement_char = getattr(self.parameters,
                                        'replacement_char', None)
        self.flatten_fields = getattr(self.parameters,
                                      'flatten_fields', ['extra'])
        if isinstance(self.flatten_fields, str):
            self.flatten_fields = self.flatten_fields.split(',')

        self.set_request_parameters()  # Not all parameters set here are used by the ES client

        self.es = Elasticsearch([{'host': self.elastic_host, 'port': self.elastic_port}],
                                http_auth=self.auth,
                                use_ssl=self.use_ssl,
                                verify_certs=self.http_verify_cert,
                                ca_certs=self.ssl_ca_certificate,
                                ssl_show_warn=self.ssl_show_warnings,
                                )

        if self.should_rotate():
            # Use rotating index names - check that the template exists
            if not self.es.indices.exists_template(name=self.elastic_index):
                raise RuntimeError("No template with the name '{}' exists on the Elasticsearch host, "
                                   "but 'rotate_index' is set. "
                                   "Have you created the template?".format(self.elastic_index))

        else:
            # Using a single named index. Check that it exists and create it if it doesn't
            if not self.es.indices.exists(self.elastic_index):
                self.es.indices.create(index=self.elastic_index, ignore=400)