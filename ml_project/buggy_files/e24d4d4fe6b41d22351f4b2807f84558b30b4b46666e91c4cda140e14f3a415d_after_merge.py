    def install_environment(
            prefix: Prefix,
            version: str,
            additional_dependencies: Sequence[str],
    ) -> None:
        directory = helpers.environment_dir(_dir, version)
        install = ('python', '-mpip', 'install', '.', *additional_dependencies)

        env_dir = prefix.path(directory)
        with clean_path_on_failure(env_dir):
            if version != C.DEFAULT:
                python = norm_version(version)
            else:
                python = os.path.realpath(sys.executable)
            _make_venv(env_dir, python)
            with in_env(prefix, version):
                helpers.run_setup_cmd(prefix, install)