    def __init__(
            self,
            name='__main__',
            server=None,
            static_folder='static',
            assets_folder=None,
            assets_url_path='/assets',
            assets_ignore='',
            include_assets_files=True,
            url_base_pathname=None,
            assets_external_path=None,
            requests_pathname_prefix=None,
            routes_pathname_prefix=None,
            compress=True,
            meta_tags=None,
            index_string=_default_index,
            external_scripts=None,
            external_stylesheets=None,
            suppress_callback_exceptions=None,
            components_cache_max_age=None,
            **kwargs):

        # pylint-disable: too-many-instance-attributes
        if 'csrf_protect' in kwargs:
            warnings.warn('''
                `csrf_protect` is no longer used,
                CSRF protection has been removed as it is no longer
                necessary.
                See https://github.com/plotly/dash/issues/141 for details.
                ''', DeprecationWarning)

        name = name if server is None else server.name
        self._assets_folder = assets_folder or os.path.join(
            flask.helpers.get_root_path(name), 'assets'
        )
        self._assets_url_path = assets_url_path

        # allow users to supply their own flask server
        self.server = server or Flask(name, static_folder=static_folder)

        if 'assets' not in self.server.blueprints:
            self.server.register_blueprint(
                flask.Blueprint('assets', 'assets',
                                static_folder=self._assets_folder,
                                static_url_path=assets_url_path))

        env_configs = _configs.env_configs()

        url_base_pathname, routes_pathname_prefix, requests_pathname_prefix = \
            _configs.pathname_configs(
                url_base_pathname,
                routes_pathname_prefix,
                requests_pathname_prefix,
                environ_configs=env_configs)

        self.url_base_pathname = url_base_pathname
        self.config = _AttributeDict({
            'suppress_callback_exceptions': _configs.get_config(
                'suppress_callback_exceptions',
                suppress_callback_exceptions, env_configs, False
            ),
            'routes_pathname_prefix': routes_pathname_prefix,
            'requests_pathname_prefix': requests_pathname_prefix,
            'include_assets_files': _configs.get_config(
                'include_assets_files',
                include_assets_files,
                env_configs,
                True),
            'assets_external_path': _configs.get_config(
                'assets_external_path', assets_external_path, env_configs, ''),
            'components_cache_max_age': int(_configs.get_config(
                'components_cache_max_age', components_cache_max_age,
                env_configs, 2678400))
        })

        # list of dependencies
        self.callback_map = {}

        self._index_string = ''
        self.index_string = index_string
        self._meta_tags = meta_tags or []
        self._favicon = None

        if compress:
            # gzip
            Compress(self.server)

        @self.server.errorhandler(exceptions.PreventUpdate)
        def _handle_error(error):
            """Handle a halted callback and return an empty 204 response"""
            print(error, file=sys.stderr)
            return ('', 204)

        # static files from the packages
        self.css = Css()
        self.scripts = Scripts()

        self._external_scripts = external_scripts or []
        self._external_stylesheets = external_stylesheets or []

        self.assets_ignore = assets_ignore

        self.registered_paths = {}

        # urls

        def add_url(name, view_func, methods=('GET',)):
            self.server.add_url_rule(
                name,
                view_func=view_func,
                endpoint=name,
                methods=list(methods)
            )

        add_url(
            '{}_dash-layout'.format(self.config['routes_pathname_prefix']),
            self.serve_layout)

        add_url(
            '{}_dash-dependencies'.format(
                self.config['routes_pathname_prefix']),
            self.dependencies)

        add_url(
            '{}_dash-update-component'.format(
                self.config['routes_pathname_prefix']),
            self.dispatch,
            ['POST'])

        add_url((
            '{}_dash-component-suites'
            '/<string:package_name>'
            '/<path:path_in_package_dist>').format(
                self.config['routes_pathname_prefix']),
                self.serve_component_suites)

        add_url(
            '{}_dash-routes'.format(self.config['routes_pathname_prefix']),
            self.serve_routes)

        add_url(
            self.config['routes_pathname_prefix'],
            self.index)

        # catch-all for front-end routes
        add_url(
            '{}<path:path>'.format(self.config['routes_pathname_prefix']),
            self.index)

        self.server.before_first_request(self._setup_server)

        self._layout = None
        self._cached_layout = None
        self.routes = []