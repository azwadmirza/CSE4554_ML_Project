def main():
    from ..base.constants import ROOT_ENV_NAME
    from ..utils import shells
    if '-h' in sys.argv or '--help' in sys.argv:
        # all execution paths sys.exit at end.
        help(sys.argv[1], sys.argv[2])

    if len(sys.argv) > 2:
        shell = sys.argv[2]
        shelldict = shells[shell]
    else:
        shelldict = {}

    if sys.argv[1] == '..activate':
        print(get_activate_path(shelldict))
        sys.exit(0)

    elif sys.argv[1] == '..deactivate.path':
        import re
        activation_path = get_activate_path(shelldict)

        if os.getenv('_CONDA_HOLD'):
            new_path = re.sub(r'%s(:?)' % re.escape(activation_path),
                              r'CONDA_PATH_PLACEHOLDER\1',
                              os.environ[str('PATH')], 1)
        else:
            new_path = re.sub(r'%s(:?)' % re.escape(activation_path), r'',
                              os.environ[str('PATH')], 1)

        print(new_path)
        sys.exit(0)

    elif sys.argv[1] == '..checkenv':
        if len(sys.argv) < 4:
            raise ArgumentError("Invalid arguments to checkenv.  Need shell and env name/path")
        if len(sys.argv) > 4:
            raise ArgumentError("did not expect more than one argument.")
        if sys.argv[3].lower() == ROOT_ENV_NAME.lower():
            # no need to check root env and try to install a symlink there
            sys.exit(0)
            # raise CondaSystemExit

        # this should throw an error and exit if the env or path can't be found.
        try:
            prefix = prefix_from_arg(sys.argv[3], shelldict=shelldict)
        except ValueError as e:
            raise CondaValueError(text_type(e))

        # Make sure an env always has the conda symlink
        try:
            from ..base.context import context
            from ..install import symlink_conda
            symlink_conda(prefix, context.root_prefix, shell)
        except (IOError, OSError) as e:
            if e.errno == errno.EPERM or e.errno == errno.EACCES:
                msg = ("Cannot activate environment {0}.\n"
                       "User does not have write access for conda symlinks."
                       .format(sys.argv[2]))
                raise CondaEnvironmentError(msg)
            raise
        sys.exit(0)
        # raise CondaSystemExit
    elif sys.argv[1] == '..changeps1':
        from ..base.context import context
        path = int(context.changeps1)

    else:
        # This means there is a bug in main.py
        raise CondaValueError("unexpected command")

    # This print is actually what sets the PATH or PROMPT variable.  The shell
    # script gets this value, and finishes the job.
    print(path)