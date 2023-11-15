    def on_profiler_state_changed(self, data):
        self.toggling_profiler = False
        self.window().toggle_profiler_button.setEnabled(True)
        self.load_profiler_tab()

        if 'profiler_file' in data:
            QMessageBox.about(self,
                              "Profiler statistics saved",
                              "The profiler data has been saved to %s." % data['profiler_file'])