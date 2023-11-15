    def checkout(
        self,
        path_info,
        hash_info,
        force=False,
        progress_callback=None,
        relink=False,
        filter_info=None,
    ):
        if path_info.scheme not in ["local", self.tree.scheme]:
            raise NotImplementedError

        failed = None
        skip = False
        if not hash_info:
            logger.warning(
                "No file hash info found for '%s'. " "It won't be created.",
                path_info,
            )
            self.safe_remove(path_info, force=force)
            failed = path_info

        elif not relink and not self.changed(path_info, hash_info):
            logger.debug("Data '%s' didn't change.", path_info)
            skip = True

        elif self.changed_cache(
            hash_info, path_info=path_info, filter_info=filter_info
        ):
            logger.warning(
                "Cache '%s' not found. File '%s' won't be created.",
                hash_info,
                path_info,
            )
            self.safe_remove(path_info, force=force)
            failed = path_info

        if failed or skip:
            if progress_callback:
                progress_callback(
                    str(path_info),
                    self.get_files_number(
                        self.tree.path_info, hash_info, filter_info
                    ),
                )
            if failed:
                raise CheckoutError([failed])
            return

        logger.debug(
            "Checking out '%s' with cache '%s'.", path_info, hash_info
        )

        return self._checkout(
            path_info,
            hash_info,
            force,
            progress_callback,
            relink,
            filter_info,
        )