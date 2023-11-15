    def download(
        self,
        from_infos,
        to_infos,
        no_progress_bar=False,
        names=None,
        resume=False,
    ):
        names = self._verify_path_args(to_infos, from_infos, names)

        for to_info, from_info, name in zip(to_infos, from_infos, names):
            if from_info.scheme != self.scheme:
                raise NotImplementedError

            if to_info.scheme != "local":
                raise NotImplementedError

            msg = "Downloading '{}' to '{}'".format(
                from_info.path, to_info.path
            )
            logger.debug(msg)

            if not name:
                name = os.path.basename(to_info.path)

            makedirs(os.path.dirname(to_info.path), exist_ok=True)

            total = self._content_length(from_info.path)

            if no_progress_bar or not total:
                cb = None
            else:
                cb = ProgressBarCallback(name, total)

            try:
                self._download_to(
                    from_info.path, to_info.path, callback=cb, resume=resume
                )

            except Exception:
                msg = "failed to download '{}'".format(from_info.path)
                logger.exception(msg)
                continue

            if not no_progress_bar:
                progress.finish_target(name)