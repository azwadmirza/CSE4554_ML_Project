    def _create_unpacked_dir(self, checksum, dir_info, unpacked_dir_info):
        self.makedirs(unpacked_dir_info)

        for entry in progress(dir_info, name="Created unpacked dir"):
            entry_cache_info = self.checksum_to_path_info(
                entry[self.PARAM_CHECKSUM]
            )
            relpath = entry[self.PARAM_RELPATH]
            self.link(
                entry_cache_info, unpacked_dir_info / relpath, "hardlink"
            )

        self.state.save(unpacked_dir_info, checksum)