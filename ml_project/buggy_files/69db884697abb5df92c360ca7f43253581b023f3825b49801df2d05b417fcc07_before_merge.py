    def initialize_discovered_page(self):
        self.window().core_manager.events_manager.discovered_channel.connect(self.on_discovered_channel)