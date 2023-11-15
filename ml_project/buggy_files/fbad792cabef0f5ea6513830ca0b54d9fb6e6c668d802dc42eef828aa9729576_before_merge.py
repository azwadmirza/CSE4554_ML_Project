    def __init__(self, parent):
        QObject.__init__(self)
        self.main = parent

        self.lsp_plugins = {}
        self.clients = {}
        self.requests = {}
        self.register_queue = {}

        # Get configurations for all LSP servers registered through
        # our Preferences
        self.configurations_for_servers = CONF.options('lsp-server')

        # Register languages to create clients for
        for language in self.configurations_for_servers:
            self.clients[language] = {
                'status': self.STOPPED,
                'config': CONF.get('lsp-server', language),
                'instance': None
            }
            self.register_queue[language] = []