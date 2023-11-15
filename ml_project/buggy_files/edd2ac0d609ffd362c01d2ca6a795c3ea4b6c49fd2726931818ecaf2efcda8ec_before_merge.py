    def on_profiler_info(self, data):
        self.profiler_enabled = (data["state"] == "STARTED")
        self.window().toggle_profiler_button.setEnabled(True)
        self.window().toggle_profiler_button.setText("%s profiler" %
                                                     ("Stop" if self.profiler_enabled else "Start"))