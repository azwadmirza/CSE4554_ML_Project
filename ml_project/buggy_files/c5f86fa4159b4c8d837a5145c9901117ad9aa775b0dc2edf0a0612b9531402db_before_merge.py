    def _download_file(
        self, from_info, to_info, name, no_progress_bar, file_mode, dir_mode
    ):
        makedirs(to_info.parent, exist_ok=True, mode=dir_mode)

        logger.debug("Downloading '%s' to '%s'", from_info, to_info)
        name = name or to_info.name

        tmp_file = tmp_fname(to_info)

        try:
            self._download(
                from_info, tmp_file, name=name, no_progress_bar=no_progress_bar
            )
        except Exception as e:
            return self._handle_transfer_exception(
                from_info, to_info, e, "download"
            )

        move(tmp_file, to_info, mode=file_mode)

        return 0