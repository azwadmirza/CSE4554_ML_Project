    def create_argv(
        self, pex_path: str, *args: str, python: Optional[PythonExecutable] = None
    ) -> Iterable[str]:
        python = python or self.bootstrap_python
        argv = [python.path] if python else []
        argv.extend((pex_path, *args))
        return argv