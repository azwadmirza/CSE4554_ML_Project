    def register_config(self) -> None:
        super().register_config()
        deps_kwargs = {"root": self.core["toxinidir"]}
        self.conf.add_config(
            keys="deps",
            of_type=RequirementsFile,
            kwargs=deps_kwargs,
            default=RequirementsFile("", **deps_kwargs),
            desc="Name of the python dependencies as specified by PEP-440",
        )
        self.core.add_config(
            keys=["skip_missing_interpreters"],
            default=True,
            of_type=bool,
            desc="skip running missing interpreters",
        )