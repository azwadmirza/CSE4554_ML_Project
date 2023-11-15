    def _checkout_dir(
        self, path_info, checksum, force, progress_callback=None
    ):
        # Create dir separately so that dir is created
        # even if there are no files in it
        if not self.exists(path_info):
            self.makedirs(path_info)

        dir_info = self.get_dir_cache(checksum)

        logger.debug("Linking directory '{}'.".format(path_info))

        for entry in dir_info:
            relpath = entry[self.PARAM_RELPATH]
            entry_checksum = entry[self.PARAM_CHECKSUM]
            entry_cache_info = self.checksum_to_path_info(entry_checksum)
            entry_info = path_info / relpath

            entry_checksum_info = {self.PARAM_CHECKSUM: entry_checksum}
            if self.changed(entry_info, entry_checksum_info):
                if self.exists(entry_info):
                    self.safe_remove(entry_info, force=force)
                self.link(entry_cache_info, entry_info)
                self.state.save(entry_info, entry_checksum)
            if progress_callback:
                progress_callback.update(str(entry_info))

        self._remove_redundant_files(path_info, dir_info, force)

        self.state.save_link(path_info)
        self.state.save(path_info, checksum)