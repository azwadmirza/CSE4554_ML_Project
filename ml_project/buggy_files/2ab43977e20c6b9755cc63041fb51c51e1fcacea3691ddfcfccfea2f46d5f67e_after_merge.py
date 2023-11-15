    def _read_info_file(self) -> None:
        if self._info_file.exists():
            try:
                with self._info_file.open(encoding="utf-8") as f:
                    info = json.load(f)
            except json.JSONDecodeError as e:
                log.error(
                    "Invalid JSON information file at path: %s\nError: %s", self._info_file, str(e)
                )
                info = {}
        else:
            info = {}
        if not isinstance(info, dict):
            log.warning(
                "Invalid top-level structure (expected dict, got %s)"
                " in JSON information file at path: %s",
                type(info).__name__,
                self._info_file,
            )
            info = {}
        self._info = info

        update_mixin(self, REPO_SCHEMA)