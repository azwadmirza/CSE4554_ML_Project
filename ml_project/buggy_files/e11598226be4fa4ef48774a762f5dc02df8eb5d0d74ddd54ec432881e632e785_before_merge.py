    def create_argv(
        self, pex_path: str, *args: str, always_use_shebang: bool = False
    ) -> Iterable[str]:
        argv = [self.bootstrap_python] if self.bootstrap_python and not always_use_shebang else []
        argv.extend((pex_path, *args))
        return argv