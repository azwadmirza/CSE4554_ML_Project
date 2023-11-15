    def start_stop_analysis_timer(self):
        self.is_analysis_done = False
        if self.realtime_analysis_enabled:
            self.analysis_timer.stop()
            self.analysis_timer.start()