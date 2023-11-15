    def guiservthread_free_space_check(self):
        free_space = get_free_space(DefaultDownloadStartupConfig.getInstance().get_dest_dir())
        self.frame.SRstatusbar.RefreshFreeSpace(free_space)

        storage_locations = defaultdict(list)
        for download in self.utility.session.get_downloads():
            if download.get_status() == DLSTATUS_DOWNLOADING:
                storage_locations[download.get_dest_dir()].append(download)

        show_message = False
        low_on_space = [
            path for path in storage_locations.keys(
            ) if 0 < get_free_space(
                path) < self.utility.read_config(
                'free_space_threshold')]
        for path in low_on_space:
            for download in storage_locations[path]:
                download.stop()
                show_message = True

        if show_message:
            wx.CallAfter(wx.MessageBox, "Tribler has detected low disk space. Related downloads have been stopped.",
                         "Error")