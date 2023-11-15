    def check_download(self):
        check = self.scan_download({"dl_limit": to_bytes(self.DL_LIMIT_PATTERN)})

        if check == "dl_limit":
            self.log_warning(self._("Free download limit reached"))
            os.remove(self.last_download)
            self.retry(wait=10800, msg=self._("Free download limit reached"))

        return super().check_download()