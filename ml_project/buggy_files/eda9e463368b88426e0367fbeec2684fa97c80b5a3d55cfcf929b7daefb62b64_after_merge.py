    def checkout(
        self,
        force=False,
        progress_callback=None,
        relink=False,
        filter_info=None,
        allow_missing=False,
        **kwargs,
    ):
        if not self.use_cache:
            if progress_callback:
                progress_callback(
                    str(self.path_info), self.get_files_number(filter_info)
                )
            return None

        try:
            return self.cache.checkout(
                self.path_info,
                self.hash_info,
                force=force,
                progress_callback=progress_callback,
                relink=relink,
                filter_info=filter_info,
                **kwargs,
            )
        except CheckoutError:
            if allow_missing:
                return None
            raise