def add_deprecated_argument(add_argument, argument_name, nargs):
    """Adds a deprecated argument with the name argument_name.

    Deprecated arguments are not shown in the help. If they are used on
    the command line, a warning is shown stating that the argument is
    deprecated and no other action is taken.

    :param callable add_argument: Function that adds arguments to an
        argument parser/group.
    :param str argument_name: Name of deprecated argument.
    :param nargs: Value for nargs when adding the argument to argparse.

    """
    class ShowWarning(argparse.Action):
        """Action to log a warning when an argument is used."""
        def __call__(self, unused1, unused2, unused3, option_string=None):
            sys.stderr.write(
                "Use of {0} is deprecated.\n".format(option_string))

    configargparse.ACTION_TYPES_THAT_DONT_NEED_A_VALUE.add(ShowWarning)
    add_argument(argument_name, action=ShowWarning,
                 help=argparse.SUPPRESS, nargs=nargs)