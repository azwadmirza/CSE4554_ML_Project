def build_help():
    parser = argparse.ArgumentParser(
        description="Command line tool to handle configuration on devices using NAPALM."
        "The script will print the diff on the screen",
        epilog="Automate all the things!!!",
    )
    parser.add_argument(
        dest="hostname",
        action="store",
        help="Host where you want to deploy the configuration.",
    )
    parser.add_argument(
        "--user",
        "-u",
        dest="user",
        action="store",
        default=getpass.getuser(),
        help="User for authenticating to the host. Default: user running the script.",
    )
    parser.add_argument(
        "--password",
        "-p",
        dest="password",
        action="store",
        help="Password for authenticating to the host."
        "If you do not provide a password in the CLI you will be prompted.",
    )
    parser.add_argument(
        "--vendor",
        "-v",
        dest="vendor",
        action="store",
        required=True,
        help="Host Operating System.",
    )
    parser.add_argument(
        "--optional_args",
        "-o",
        dest="optional_args",
        action="store",
        help="String with comma separated key=value pairs passed via optional_args to the driver.",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help="Enables debug mode; more verbosity.",
    )
    subparser = parser.add_subparsers(title="actions")

    config = subparser.add_parser("configure", help="Perform a configuration operation")
    config.set_defaults(which="config")
    config.add_argument(
        dest="config_file",
        action="store",
        help="File containing the configuration you want to deploy.",
    )
    config.add_argument(
        "--strategy",
        "-s",
        dest="strategy",
        action="store",
        choices=["replace", "merge"],
        default="replace",
        help="Strategy to use to deploy configuration. Default: replace.",
    )
    config.add_argument(
        "--dry-run",
        "-d",
        dest="dry_run",
        action="store_true",
        default=None,
        help="Only returns diff, it does not deploy the configuration.",
    )

    call = subparser.add_parser("call", help="Call a napalm method")
    call.set_defaults(which="call")
    call.add_argument(dest="method", action="store", help="Run this method")
    call.add_argument(
        "--method-kwargs",
        "-k",
        dest="method_kwargs",
        action="store",
        help='kwargs to pass to the method. For example: "destination=1.1.1.1,protocol=bgp"',
    )

    validate = subparser.add_parser("validate", help="Validate configuration/state")
    validate.set_defaults(which="validate")
    validate.add_argument(
        dest="validation_file",
        action="store",
        help="Validation file containing resources derised states",
    )
    args = parser.parse_args()

    if args.password is None:
        password = getpass.getpass("Enter password: ")
        setattr(args, "password", password)

    return args