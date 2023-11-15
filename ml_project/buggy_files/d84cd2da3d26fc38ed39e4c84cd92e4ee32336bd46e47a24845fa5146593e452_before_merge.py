    def __init__(self, unsupported_settings: Dict[str, Dict[str, str]]):
        errors = "\n".join(
            self._format_option(name, **option) for name, option in unsupported_settings.items()
        )

        super().__init__(
            "isort was provided settings that it doesn't support:\n\n"
            f"{errors}\n\n"
            "For a complete and up-to-date listing of supported settings see: "
            "https://pycqa.github.io/isort/docs/configuration/options/.\n"
        )
        self.unsupported_settings = unsupported_settings