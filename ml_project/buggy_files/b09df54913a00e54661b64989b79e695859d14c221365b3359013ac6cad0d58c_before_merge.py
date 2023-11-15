def main(args: Optional[List[str]]=NotProvided, stdin: Optional[IO]=NotProvided, pwd: Optional[str]=None) -> None:
    args = sys.argv[1:] if args is NotProvided else args
    stdin = sys.stdin if stdin is NotProvided else stdin

    subcommands = list_subcommands()
    parser = argparse.ArgumentParser(
        prog=__command__,
        description='ArchiveBox: The self-hosted internet archive',
        add_help=False,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--help', '-h',
        action='store_true',
        help=subcommands['help'],
    )
    group.add_argument(
        '--version',
        action='store_true',
        help=subcommands['version'],
    )
    group.add_argument(
        "subcommand",
        type=str,
        help= "The name of the subcommand to run",
        nargs='?',
        choices=subcommands.keys(),
        default=None,
    )
    parser.add_argument(
        "subcommand_args",
        help="Arguments for the subcommand",
        nargs=argparse.REMAINDER,
    )
    command = parser.parse_args(args or ())

    if command.help or command.subcommand is None:
        command.subcommand = 'help'
    elif command.version:
        command.subcommand = 'version'
    
    if command.subcommand not in ('help', 'version', 'status'):
        from ..logging import log_cli_command

        log_cli_command(
            subcommand=command.subcommand,
            subcommand_args=command.subcommand_args,
            stdin=stdin,
            pwd=pwd or OUTPUT_DIR
        )

    run_subcommand(
        subcommand=command.subcommand,
        subcommand_args=command.subcommand_args,
        stdin=stdin,
        pwd=pwd or OUTPUT_DIR,
    )