    def _process(
        self,
        named_cache,
        remote,
        jobs=None,
        show_checksums=False,
        download=False,
    ):
        logger.debug(
            "Preparing to {} '{}'".format(
                "download data from" if download else "upload data to",
                remote.path_info,
            )
        )

        if download:
            func = partial(
                _log_exceptions(remote.tree.download, "download"),
                dir_mode=self.tree.dir_mode,
                file_mode=self.tree.file_mode,
            )
            status = STATUS_DELETED
            desc = "Downloading"
        else:
            func = _log_exceptions(remote.tree.upload, "upload")
            status = STATUS_NEW
            desc = "Uploading"

        if jobs is None:
            jobs = remote.JOBS

        dir_status, file_status, dir_contents = self._status(
            named_cache,
            remote,
            jobs=jobs,
            show_checksums=show_checksums,
            download=download,
        )

        dir_plans = self._get_plans(download, remote, dir_status, status)
        file_plans = self._get_plans(download, remote, file_status, status)

        total = len(dir_plans[0]) + len(file_plans[0])
        if total == 0:
            return 0

        with Tqdm(total=total, unit="file", desc=desc) as pbar:
            func = pbar.wrap_fn(func)
            with ThreadPoolExecutor(max_workers=jobs) as executor:
                if download:
                    fails = sum(executor.map(func, *dir_plans))
                    fails += sum(executor.map(func, *file_plans))
                else:
                    # for uploads, push files first, and any .dir files last

                    file_futures = {}
                    for from_info, to_info, name, checksum in zip(*file_plans):
                        file_futures[checksum] = executor.submit(
                            func, from_info, to_info, name
                        )
                    dir_futures = {}
                    for from_info, to_info, name, dir_checksum in zip(
                        *dir_plans
                    ):
                        wait_futures = {
                            future
                            for file_checksum, future in file_futures.items()
                            if file_checksum in dir_contents[dir_checksum]
                        }
                        dir_futures[dir_checksum] = executor.submit(
                            self._dir_upload,
                            func,
                            wait_futures,
                            from_info,
                            to_info,
                            name,
                        )
                    fails = sum(
                        future.result()
                        for future in concat(
                            file_futures.values(), dir_futures.values()
                        )
                    )

        if fails:
            if download:
                remote.index.clear()
                raise DownloadError(fails)
            raise UploadError(fails)

        if not download:
            # index successfully pushed dirs
            for dir_checksum, future in dir_futures.items():
                if future.result() == 0:
                    file_checksums = dir_contents[dir_checksum]
                    logger.debug(
                        "Indexing pushed dir '{}' with "
                        "'{}' nested files".format(
                            dir_checksum, len(file_checksums)
                        )
                    )
                    remote.index.update([dir_checksum], file_checksums)

        return len(dir_plans[0]) + len(file_plans[0])