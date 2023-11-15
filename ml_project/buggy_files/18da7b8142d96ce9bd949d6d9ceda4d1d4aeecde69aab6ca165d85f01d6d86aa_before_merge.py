    def _create_web_factory(self, config):

        options = config.get('options', {})

        # create Twisted Web root resource
        if '/' in config['paths']:
            root_config = config['paths']['/']
            root = self._create_resource(root_config, nested=False)
        else:
            root = Resource404(self._templates, b'')

        # create Twisted Web resources on all non-root paths configured
        self._add_paths(root, config.get('paths', {}))

        # create the actual transport factory
        transport_factory = Site(
            root,
            timeout=options.get('client_timeout', None),
        )
        transport_factory.noisy = False

        # we override this factory so that we can inject
        # _LessNoisyHTTPChannel to avoid info-level logging on timing
        # out web clients (which happens all the time).
        def channel_protocol_factory():
            return _GenericHTTPChannelProtocol(_LessNoisyHTTPChannel())
        transport_factory.protocol = channel_protocol_factory

        # Web access logging
        if not options.get('access_log', False):
            transport_factory.log = lambda _: None

        # Traceback rendering
        transport_factory.displayTracebacks = options.get('display_tracebacks', False)

        # HSTS
        if options.get('hsts', False):
            if 'tls' in config['endpoint']:
                hsts_max_age = int(options.get('hsts_max_age', 31536000))
                transport_factory.requestFactory = createHSTSRequestFactory(transport_factory.requestFactory, hsts_max_age)
            else:
                self.log.warn("Warning: HSTS requested, but running on non-TLS - skipping HSTS")

        return transport_factory