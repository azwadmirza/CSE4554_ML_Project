    def register_config(self) -> None:
        super().register_config()
        self.conf.add_config(
            keys="deps",
            of_type=RequirementsFile,
            default=RequirementsFile(""),
            desc="Name of the python dependencies as specified by PEP-440",
        )
        self.core.add_config(
            keys=["skip_missing_interpreters"],
            default=True,
            of_type=bool,
            desc="skip running missing interpreters",
        )