    def __init__(self, parent):
        QObject.__init__(self)
        self.main = parent

        self.lsp_plugins = {}
        self.clients = {}
        self.requests = {}
        self.register_queue = {}
        self.python_config = PYTHON_CONFIG.copy()

        # Register languages to create clients for
        for language in self.get_languages():
            self.clients[language] = {
                'status': self.STOPPED,
                'config': self.get_language_config(language),
                'instance': None
            }
            self.register_queue[language] = []