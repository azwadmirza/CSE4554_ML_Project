    def __init__(self, coresys: CoreSys, addon: AnyAddon) -> None:
        """Initialize Supervisor add-on builder."""
        self.coresys: CoreSys = coresys
        self.addon = addon

        super().__init__(
            find_one_filetype(
                self.addon.path_location, "build", FILE_SUFFIX_CONFIGURATION
            ),
            SCHEMA_BUILD_CONFIG,
        )