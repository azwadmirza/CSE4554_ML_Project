    def process(self, operation: Operation):
        filepath = get_absolute_path(self._root_dir, operation.filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f'Could not find {filepath}')
        if not os.path.isfile(filepath):
            raise ValueError(f'Not a file: {filepath}')

        self.log.debug(f'Processing: {filepath}')
        file_dir = os.path.dirname(filepath)
        argv = self._create_execute_command(filepath, file_dir)
        envs = operation.env_vars_as_dict(self.log)
        try:
            run(argv, cwd=file_dir, env=envs, check=True)
        except Exception as ex:
            raise RuntimeError(f'Internal error executing {filepath}: {ex}') from ex