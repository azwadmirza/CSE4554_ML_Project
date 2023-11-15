    def initialize_discovered_page(self):
        if not self.initialized:
            self.window().core_manager.events_manager.discovered_channel.connect(self.on_discovered_channel)
            self.initialized = True