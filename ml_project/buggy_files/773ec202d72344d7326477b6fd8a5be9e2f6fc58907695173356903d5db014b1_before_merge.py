    def scan_path_gaze_for_frame(self, frame):
        if self.timeframe == 0.0:
            return None

        if not self._gaze_data_store.is_valid or not self._gaze_data_store.is_complete:
            if not self.is_active:
                self._trigger_immediate_scan_path_calculation()
            return None

        timestamp_cutoff = frame.timestamp - self.timeframe

        gaze_data = self._gaze_data_store.gaze_data
        gaze_data = gaze_data[gaze_data.frame_index == frame.index]
        gaze_data = gaze_data[gaze_data.timestamp > timestamp_cutoff]

        return gaze_data