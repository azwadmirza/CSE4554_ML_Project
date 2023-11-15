    def process(self, operation: Operation):
        filepath = self.get_valid_filepath(operation.filename)

        file_dir = os.path.dirname(filepath)
        file_name = os.path.basename(filepath)

        self.log.debug(f'Processing python script: {filepath}')

        argv = ['python3', filepath, '--PYTHONHOME', file_dir]

        envs = os.environ  # Make sure this process's env is "available" in subprocess
        envs.update(operation.env_vars_as_dict())
        t0 = time.time()
        try:
            run(argv, cwd=file_dir, env=envs, check=True)
        except Exception as ex:
            raise RuntimeError(f'Internal error executing {filepath}: {ex}') from ex

        t1 = time.time()
        duration = (t1 - t0)
        self.log.debug(f'Execution of {file_name} took {duration:.3f} secs.')