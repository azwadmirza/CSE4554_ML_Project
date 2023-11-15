    def _read_info_file(self) -> None:
        super()._read_info_file()

        update_mixin(self, INSTALLABLE_SCHEMA)
        if self.type == InstallableType.SHARED_LIBRARY:
            self.hidden = True