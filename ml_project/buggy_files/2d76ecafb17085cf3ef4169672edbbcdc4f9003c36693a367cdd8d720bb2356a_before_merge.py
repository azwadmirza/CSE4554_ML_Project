    def build_venv(cls, path, executable=None):
        if executable is not None:
            # Create virtualenv by using an external executable
            try:
                p = subprocess.Popen(
                    list_to_shell_command([executable, "-"]),
                    stdin=subprocess.PIPE,
                    shell=True,
                )
                p.communicate(encode(CREATE_VENV_COMMAND.format(path)))
            except CalledProcessError as e:
                raise EnvCommandError(e)

            return

        try:
            from venv import EnvBuilder

            # use the same defaults as python -m venv
            if os.name == "nt":
                use_symlinks = False
            else:
                use_symlinks = True

            builder = EnvBuilder(with_pip=True, symlinks=use_symlinks)
            build = builder.create
        except ImportError:
            # We fallback on virtualenv for Python 2.7
            from virtualenv import create_environment

            build = create_environment

        build(path)