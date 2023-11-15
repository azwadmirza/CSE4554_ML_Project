    def __init__(self, parent, server_args_fmt='',
                 server_settings={}, external_server=False,
                 folder=getcwd_or_home(), language='python',
                 plugin_configurations={}):
        QObject.__init__(self)
        # LSPMethodProviderMixIn.__init__(self)
        self.manager = parent
        self.zmq_in_socket = None
        self.zmq_out_socket = None
        self.zmq_in_port = None
        self.zmq_out_port = None
        self.transport_client = None
        self.language = language

        self.initialized = False
        self.ready_to_close = False
        self.request_seq = 1
        self.req_status = {}
        self.plugin_registry = {}
        self.watched_files = {}
        self.req_reply = {}

        self.transport_args = [sys.executable, '-u',
                               osp.join(LOCATION, 'transport', 'main.py')]
        self.external_server = external_server

        self.folder = folder
        self.plugin_configurations = plugin_configurations
        self.client_capabilites = CLIENT_CAPABILITES
        self.server_capabilites = SERVER_CAPABILITES
        self.context = zmq.Context()

        server_args = server_args_fmt % (server_settings)
        # transport_args = self.local_server_fmt % (server_settings)
        # if self.external_server:
        transport_args = self.external_server_fmt % (server_settings)

        self.server_args = [sys.executable, '-m', server_settings['cmd']]
        self.server_args += server_args.split(' ')
        self.transport_args += transport_args.split(' ')
        self.transport_args += ['--folder', folder]
        self.transport_args += ['--transport-debug', str(get_debug_level())]