    def on_received_downloads(self, downloads):
        if not downloads:
            return  # This might happen when closing Tribler

        bytes_max = self.window().tribler_settings["credit_mining"]["max_disk_space"]
        bytes_used = 0
        total_up = total_down = 0
        for download in downloads["downloads"]:
            if download["credit_mining"] and \
                    download["status"] in ("DLSTATUS_DOWNLOADING", "DLSTATUS_SEEDING",
                                           "DLSTATUS_STOPPED", "DLSTATUS_STOPPED_ON_ERROR"):
                bytes_used += download["progress"] * download["size"]
                total_up += download["total_up"]
                total_down += download["total_down"]

        self.window().token_mining_upload_amount_label.setText(format_size(total_up))
        self.window().token_mining_download_amount_label.setText(format_size(total_down))
        self.window().token_mining_disk_usage_label.setText("%s / %s" % (format_size(float(bytes_used)),
                                                                         format_size(float(bytes_max))))

        self.push_data_to_plot(total_up, total_down)
        self.trust_plot.plot_data = self.plot_data
        self.trust_plot.compute_initial_figure()

        self.schedule_downloads_timer()

        # Matplotlib is leaking memory on re-plotting. Refer: https://github.com/matplotlib/matplotlib/issues/8528
        # Note that gc is called every 10 minutes.
        if self.gc_timer == GC_TIMEOUT:
            gc.collect()
            self.gc_timer = 0
        else:
            self.gc_timer += 1