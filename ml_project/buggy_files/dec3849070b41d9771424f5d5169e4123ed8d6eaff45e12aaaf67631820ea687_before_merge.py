    def __init__(self, parent, plugins=['lsp', 'kite', 'fallback']):
        SpyderCompletionPlugin.__init__(self, parent)
        self.clients = {}
        self.requests = {}
        self.language_status = {}
        self.started = False
        self.req_id = 0
        self.collection_mutex = QMutex()

        for plugin in plugins:
            if plugin in self.BASE_PLUGINS:
                Plugin = self.BASE_PLUGINS[plugin]
                plugin_client = Plugin(self.main)
                self.register_completion_plugin(plugin_client)