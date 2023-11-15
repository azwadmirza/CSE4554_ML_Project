    def checkout(
        self,
        force=False,
        progress_callback=None,
        relink=False,
        filter_info=None,
    ):
        if not self.use_cache:
            if progress_callback:
                progress_callback(
                    str(self.path_info), self.get_files_number(filter_info)
                )
            return None

        return self.cache.checkout(
            self.path_info,
            self.hash_info.to_dict(),
            force=force,
            progress_callback=progress_callback,
            relink=relink,
            filter_info=filter_info,
        )