    def check_disk_space(self):
        if not self.check_mining_directory():
            return

        # Note that we have a resource monitor that monitors the disk where the state-directory resides.
        # However, since the credit mining directory can be on a different disk, we query the disk space ourselves.
        is_low = self.get_free_disk_space() < self.settings.low_disk_space
        if self.upload_mode != is_low:
            self._logger.info('Setting upload mode to %s', is_low)

            self.upload_mode = is_low

            def set_upload_mode(handle):
                handle.set_upload_mode(is_low)

            for download in self.session.get_downloads():
                if download.get_credit_mining():
                    download.get_handle().addCallback(set_upload_mode)