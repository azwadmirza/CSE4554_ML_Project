    def _read_info_file(self) -> None:
        super()._read_info_file()

        if self._info_file.exists():
            self._process_info_file()