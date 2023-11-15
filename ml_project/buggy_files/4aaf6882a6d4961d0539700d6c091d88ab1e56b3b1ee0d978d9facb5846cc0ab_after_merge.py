def _add_run(subparsers):
    p = subparsers.add_parser(
        "run",
        formatter_class=LineWrapRawTextHelpFormatter,
        help=(
            "Download the latest version of a package to a temporary virtual environment, "
            "then run an app from it. Also compatible with local `__pypackages__` "
            "directory (experimental)."
        ),
        description=textwrap.dedent(
            f"""
        Download the latest version of a package to a temporary virtual environment,
        then run an app from it. The environment will be cached
        and re-used for up to {constants.TEMP_VENV_EXPIRATION_THRESHOLD_DAYS} days. This
        means subsequent calls to 'run' for the same package will be faster
        since they can re-use the cached Virtual Environment.

        In support of PEP 582 'run' will use apps found in a local __pypackages__
         directory, if present. Please note that this behavior is experimental,
         and is a acts as a companion tool to pythonloc. It may be modified or
         removed in the future. See https://github.com/cs01/pythonloc.
        """
        ),
    )
    p.add_argument(
        "--no-cache",
        action="store_true",
        help="Do not re-use cached virtual environment if it exists",
    )
    p.add_argument("app", help="app/package name")
    p.add_argument(
        "appargs",
        nargs=argparse.REMAINDER,
        help="arguments passed to the application when it is invoked",
        default=[],
    )
    p.add_argument(
        "--pypackages",
        action="store_true",
        help="Require app to be run from local __pypackages__ directory",
    )
    p.add_argument("--spec", help=SPEC_HELP)
    p.add_argument("--verbose", action="store_true")
    p.add_argument(
        "--python",
        default=constants.DEFAULT_PYTHON,
        help="The Python version to run package's CLI app with. Must be v3.5+.",
    )
    add_pip_venv_args(p)