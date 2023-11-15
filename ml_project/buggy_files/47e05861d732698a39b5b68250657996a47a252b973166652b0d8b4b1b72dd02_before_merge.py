    def upload(self, from_info, to_info, name=None, no_progress_bar=False):
        if not hasattr(self, "_upload"):
            raise RemoteActionNotImplemented("upload", self.scheme)

        if to_info.scheme != self.scheme:
            raise NotImplementedError

        if from_info.scheme != "local":
            raise NotImplementedError

        logger.debug("Uploading '%s' to '%s'", from_info, to_info)

        name = name or from_info.name

        try:
            self._upload(
                from_info.fspath,
                to_info,
                name=name,
                no_progress_bar=no_progress_bar,
            )
        except Exception as e:
            return self._handle_transfer_exception(
                from_info, to_info, e, "upload"
            )

        return 0