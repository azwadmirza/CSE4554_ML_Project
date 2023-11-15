    def __init__(
        self,
        username,
        project_id,
        auth_url,
        region_name=None,
        password=None,
        os_auth_plugin=None,
        **kwargs
    ):
        '''
        Set up nova credentials
        '''
        self.kwargs = kwargs.copy()

        if not novaclient.base.Manager._hooks_map:
            self.extensions = client.discover_extensions('1.1')
            for extension in self.extensions:
                extension.run_hooks('__pre_parse_args__')
            self.kwargs['extensions'] = self.extensions

        self.kwargs['username'] = username
        self.kwargs['project_id'] = project_id
        self.kwargs['auth_url'] = auth_url
        self.kwargs['region_name'] = region_name
        self.kwargs['service_type'] = 'compute'

        # used in novaclient extensions to see if they are rackspace or not, to know if it needs to load
        # the hooks for that extension or not.  This is cleaned up by sanatize_novaclient
        self.kwargs['os_auth_url'] = auth_url

        if os_auth_plugin is not None:
            novaclient.auth_plugin.discover_auth_systems()
            auth_plugin = novaclient.auth_plugin.load_plugin(os_auth_plugin)
            self.kwargs['auth_plugin'] = auth_plugin
            self.kwargs['auth_system'] = os_auth_plugin

        if not self.kwargs.get('api_key', None):
            self.kwargs['api_key'] = password

        # This has to be run before sanatize_novaclient before extra variables are cleaned out.
        if hasattr(self, 'extensions'):
            # needs an object, not a dictionary
            self.kwargstruct = KwargsStruct(**self.kwargs)
            for extension in self.extensions:
                extension.run_hooks('__post_parse_args__', self.kwargstruct)
            self.kwargs = self.kwargstruct.__dict__

        self.kwargs = sanatize_novaclient(self.kwargs)

        # Requires novaclient version >= 2.6.1
        self.kwargs['version'] = str(kwargs.get('version', 2))

        conn = client.Client(**self.kwargs)
        try:
            conn.client.authenticate()
        except novaclient.exceptions.AmbiguousEndpoints:
            raise SaltCloudSystemExit(
                "Nova provider requires a 'region_name' to be specified"
            )

        self.kwargs['auth_token'] = conn.client.auth_token
        self.catalog = conn.client.service_catalog.catalog['access']['serviceCatalog']

        if region_name is not None:
            servers_endpoints = get_entry(self.catalog, 'type', 'compute')['endpoints']
            self.kwargs['bypass_url'] = get_entry(
                servers_endpoints,
                'region',
                region_name
            )['publicURL']

        self.compute_conn = client.Client(**self.kwargs)

        volume_endpoints = get_entry(self.catalog, 'type', 'volume', raise_error=False).get('endpoints', {})
        if volume_endpoints:
            if region_name is not None:
                self.kwargs['bypass_url'] = get_entry(
                    volume_endpoints,
                    'region',
                    region_name
                )['publicURL']

            self.volume_conn = client.Client(**self.kwargs)
            if hasattr(self, 'extensions'):
                self.expand_extensions()
        else:
            self.volume_conn = None