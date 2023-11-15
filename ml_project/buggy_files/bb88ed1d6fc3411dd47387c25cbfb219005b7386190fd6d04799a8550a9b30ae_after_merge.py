def py_interface(
        _dir: str,
        _make_venv: Callable[[str, str], None],
) -> Tuple[
    Callable[[Prefix, str], ContextManager[None]],
    Callable[[Prefix, str], bool],
    Callable[[Hook, Sequence[str], bool], Tuple[int, bytes]],
    Callable[[Prefix, str, Sequence[str]], None],
]:
    @contextlib.contextmanager
    def in_env(
            prefix: Prefix,
            language_version: str,
    ) -> Generator[None, None, None]:
        envdir = prefix.path(helpers.environment_dir(_dir, language_version))
        with envcontext(get_env_patch(envdir)):
            yield

    def healthy(prefix: Prefix, language_version: str) -> bool:
        envdir = helpers.environment_dir(_dir, language_version)
        exe_name = 'python.exe' if sys.platform == 'win32' else 'python'
        py_exe = prefix.path(bin_dir(envdir), exe_name)
        with in_env(prefix, language_version):
            retcode, _, _ = cmd_output_b(
                py_exe, '-c', 'import ctypes, datetime, io, os, ssl, weakref',
                cwd='/',
                retcode=None,
            )
        return retcode == 0

    def run_hook(
            hook: Hook,
            file_args: Sequence[str],
            color: bool,
    ) -> Tuple[int, bytes]:
        with in_env(hook.prefix, hook.language_version):
            return helpers.run_xargs(hook, hook.cmd, file_args, color=color)

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

    return in_env, healthy, run_hook, install_environment