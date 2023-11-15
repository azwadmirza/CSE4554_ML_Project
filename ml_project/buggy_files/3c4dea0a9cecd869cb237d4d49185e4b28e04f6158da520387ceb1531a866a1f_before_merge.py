    def refresh_memory_plot(self):
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("debug/memory_history", self.on_core_memory_history)