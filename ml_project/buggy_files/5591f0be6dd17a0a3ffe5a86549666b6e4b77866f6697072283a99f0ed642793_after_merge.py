def main():
    from ..base.constants import ROOT_ENV_NAME

    sys_argv = tuple(ensure_text_type(s) for s in sys.argv)

    if '-h' in sys_argv or '--help' in sys_argv:
        # all execution paths sys.exit at end.
        help(sys_argv[1], sys_argv[2])

    if len(sys_argv) > 2:
        shell = sys_argv[2]
    else:
        shell = ''

    if regex.match('^..(?:de|)activate$', sys_argv[1]):
        arg_num = len(sys_argv)
        if arg_num != 4:
            num_expected = 2
            if arg_num < 4:
                raise TooFewArgumentsError(num_expected, arg_num - num_expected,
                                           "{} expected exactly two arguments:\
                                            shell and env name".format(sys_argv[1]))
            if arg_num > 4:
                raise TooManyArgumentsError(num_expected, arg_num - num_expected, sys_argv[2:],
                                            "{} expected exactly two arguments:\
                                             shell and env name".format(sys_argv[1]))

    if sys_argv[1] == '..activate':
        print(get_activate_path(sys_argv[3], shell))
        sys.exit(0)

    elif sys_argv[1] == '..deactivate.path':
        activation_path = get_activate_path(sys_argv[3], shell)

        if os.getenv('_CONDA_HOLD'):
            new_path = regex.sub(r'%s(:?)' % regex.escape(activation_path),
                                 r'CONDA_PATH_PLACEHOLDER\1',
                                 os.environ[str('PATH')], 1)
        else:
            new_path = regex.sub(r'%s(:?)' % regex.escape(activation_path), r'',
                                 os.environ[str('PATH')], 1)

        print(new_path)
        sys.exit(0)

    elif sys_argv[1] == '..checkenv':
        if len(sys_argv) < 4:
            raise ArgumentError("Invalid arguments to checkenv.  Need shell and env name/path")
        if len(sys_argv) > 4:
            raise ArgumentError("did not expect more than one argument.")
        if sys_argv[3].lower() == ROOT_ENV_NAME.lower():
            # no need to check root env and try to install a symlink there
            sys.exit(0)
            # raise CondaSystemExit

        # this should throw an error and exit if the env or path can't be found.
        try:
            prefix = prefix_from_arg(sys_argv[3], shell)
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
                       .format(sys_argv[2]))
                raise CondaEnvironmentError(msg)
            raise
        sys.exit(0)
        # raise CondaSystemExit
    elif sys_argv[1] == '..changeps1':
        from ..base.context import context
        path = int(context.changeps1)

    else:
        # This means there is a bug in main.py
        raise CondaValueError("unexpected command")

    # This print is actually what sets the PATH or PROMPT variable.  The shell
    # script gets this value, and finishes the job.
    print(path)