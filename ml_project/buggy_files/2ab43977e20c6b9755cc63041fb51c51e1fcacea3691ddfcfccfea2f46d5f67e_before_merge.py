    def _read_info_file(self) -> None:
        if not (self._info_file.exists() or self._info_file.is_file()):
            return

        try:
            with self._info_file.open(encoding="utf-8") as f:
                info = json.load(f)
        except json.JSONDecodeError:
            return
        else:
            self._info = info

        try:
            author = tuple(info.get("author", []))
        except ValueError:
            author = ()
        self.author = author

        self.install_msg = info.get("install_msg")
        self.short = info.get("short")
        self.description = info.get("description")