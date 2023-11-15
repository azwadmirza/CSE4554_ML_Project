def configure_parser_config(sub_parsers):
    descr = dedent("""
    Modify configuration values in .condarc.  This is modeled after the git
    config command.  Writes to the user .condarc file (%s) by default.

    """) % user_rc_path

    # Note, the extra whitespace in the list keys is on purpose. It's so the
    # formatting from help2man is still valid YAML (otherwise it line wraps the
    # keys like "- conda - defaults"). Technically the parser here still won't
    # recognize it because it removes the indentation, but at least it will be
    # valid.
    additional_descr = """
    See `conda config --describe` or %s/docs/config.html
    for details on all the options that can go in .condarc.

    Examples:

    Display all configuration values as calculated and compiled:

        conda config --show

    Display all identified configuration sources:

        conda config --show-sources

    Describe all available configuration options:

        conda config --describe

    Add the conda-canary channel:

        conda config --add channels conda-canary

    Set the output verbosity to level 3 (highest):

        conda config --set verbosity 3

    Get the channels defined in the system .condarc:

        conda config --get channels --system

    Add the 'foo' Binstar channel:

        conda config --add channels foo

    Disable the 'show_channel_urls' option:

        conda config --set show_channel_urls no
    """ % CONDA_HOMEPAGE_URL

    p = sub_parsers.add_parser(
        'config',
        description=descr,
        help=descr,
        epilog=additional_descr,
    )
    add_parser_json(p)

    # TODO: use argparse.FileType
    location = p.add_mutually_exclusive_group()
    location.add_argument(
        "--system",
        action="store_true",
        help="""Write to the system .condarc file ({system}). Otherwise writes to the user
        config file ({user}).""".format(system=sys_rc_path,
                                        user=user_rc_path),
    )
    location.add_argument(
        "--env",
        action="store_true",
        help="Write to the active conda environment .condarc file (%s). "
             "If no environment is active, write to the user config file (%s)."
             "" % (os.getenv('CONDA_PREFIX', "<no active environment>"), user_rc_path),
    )
    location.add_argument(
        "--file",
        action="store",
        help="""Write to the given file. Otherwise writes to the user config file ({user})
or the file path given by the 'CONDARC' environment variable, if it is set
(default: %(default)s).""".format(user=user_rc_path),
        default=os.environ.get('CONDARC', user_rc_path)
    )

    # XXX: Does this really have to be mutually exclusive. I think the below
    # code will work even if it is a regular group (although combination of
    # --add and --remove with the same keys will not be well-defined).
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--show",
        nargs='*',
        default=None,
        help="Display configuration values as calculated and compiled. "
             "If no arguments given, show information for all configuration values.",
    )
    action.add_argument(
        "--show-sources",
        action="store_true",
        help="Display all identified configuration sources.",
    )
    action.add_argument(
        "--validate",
        action="store_true",
        help="Validate all configuration sources.",
    )
    action.add_argument(
        "--describe",
        nargs='*',
        default=None,
        help="Describe given configuration parameters. If no arguments given, show "
             "information for all configuration parameters.",
    )
    action.add_argument(
        "--write-default",
        action="store_true",
        help="Write the default configuration to a file. "
             "Equivalent to `conda config --describe > ~/.condarc` "
             "when no --env, --system, or --file flags are given.",
    )
    action.add_argument(
        "--get",
        nargs='*',
        action="store",
        help="Get a configuration value.",
        default=None,
        metavar='KEY',
    )
    action.add_argument(
        "--append",
        nargs=2,
        action="append",
        help="""Add one configuration value to the end of a list key.""",
        default=[],
        metavar=('KEY', 'VALUE'),
    )
    action.add_argument(
        "--prepend", "--add",
        nargs=2,
        action="append",
        help="""Add one configuration value to the beginning of a list key.""",
        default=[],
        metavar=('KEY', 'VALUE'),
    )
    action.add_argument(
        "--set",
        nargs=2,
        action="append",
        help="""Set a boolean or string key""",
        default=[],
        metavar=('KEY', 'VALUE'),
    )
    action.add_argument(
        "--remove",
        nargs=2,
        action="append",
        help="""Remove a configuration value from a list key. This removes
    all instances of the value.""",
        default=[],
        metavar=('KEY', 'VALUE'),
    )
    action.add_argument(
        "--remove-key",
        nargs=1,
        action="append",
        help="""Remove a configuration key (and all its values).""",
        default=[],
        metavar="KEY",
    )
    action.add_argument(
        "--stdin",
        action="store_true",
        help="Apply configuration information given in yaml format piped through stdin.",
    )

    p.add_argument(
        "-f", "--force",
        action="store_true",
        default=NULL,
        help=SUPPRESS,  # TODO: No longer used.  Remove in a future release.
    )

    p.set_defaults(func='.main_config.execute')