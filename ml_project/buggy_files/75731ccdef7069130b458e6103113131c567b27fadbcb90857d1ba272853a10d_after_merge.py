def py_interface(_dir, _make_venv):
    @contextlib.contextmanager
    def in_env(prefix, language_version):
        envdir = prefix.path(helpers.environment_dir(_dir, language_version))
        with envcontext(get_env_patch(envdir)):
            yield

    def healthy(prefix, language_version):
        with in_env(prefix, language_version):
            retcode, _, _ = cmd_output(
                'python', '-c',
                'import ctypes, datetime, io, os, ssl, weakref',
                retcode=None,
                encoding=None,
            )
        return retcode == 0

    def run_hook(hook, file_args):
        with in_env(hook.prefix, hook.language_version):
            return helpers.run_xargs(hook, helpers.to_cmd(hook), file_args)

    def install_environment(prefix, version, additional_dependencies):
        additional_dependencies = tuple(additional_dependencies)
        directory = helpers.environment_dir(_dir, version)

        env_dir = prefix.path(directory)
        with clean_path_on_failure(env_dir):
            if version != C.DEFAULT:
                python = norm_version(version)
            else:
                python = os.path.realpath(sys.executable)
            _make_venv(env_dir, python)
            with in_env(prefix, version):
                helpers.run_setup_cmd(
                    prefix, ('pip', 'install', '.') + additional_dependencies,
                )

    return in_env, healthy, run_hook, install_environment