    def update_item(self):
        self.setText(0, self.download_info["name"])
        self.setText(1, format_size(float(self.download_info["size"])))

        try:
            self.progress_slider.setValue(int(self.download_info["progress"] * 100))
        except RuntimeError:
            self._logger.error("The underlying GUI widget has already been removed.")

        if self.download_info["vod_mode"]:
            self.setText(3, "Streaming")
        else:
            self.setText(3, DLSTATUS_STRINGS[eval(self.download_info["status"])])
        self.setText(4, str(self.download_info["num_seeds"]))
        self.setText(5, str(self.download_info["num_peers"]))
        self.setText(6, format_speed(self.download_info["speed_down"]))
        self.setText(7, format_speed(self.download_info["speed_up"]))
        self.setText(8, "%.3f" % float(self.download_info["ratio"]))
        self.setText(9, "yes" if self.download_info["anon_download"] else "no")
        self.setText(10, str(self.download_info["hops"]) if self.download_info["anon_download"] else "-")
        self.setText(12, datetime.fromtimestamp(int(self.download_info["time_added"])).strftime('%Y-%m-%d %H:%M'))

        eta_text = "-"
        if self.get_raw_download_status() == DLSTATUS_DOWNLOADING:
            eta_text = duration_to_string(self.download_info["eta"])
        self.setText(11, eta_text)