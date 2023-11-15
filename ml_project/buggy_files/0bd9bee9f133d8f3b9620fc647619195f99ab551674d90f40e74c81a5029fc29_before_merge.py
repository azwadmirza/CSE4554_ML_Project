    def refresh_cpu_plot(self):
        self.request_mgr = TriblerRequestManager()
        self.request_mgr.perform_request("debug/cpu_history", self.on_core_cpu_history)