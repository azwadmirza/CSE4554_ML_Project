def configure_parser(sub_parsers):
    config_parser = sub_parsers.add_parser(
        'config',
        formatter_class=RawDescriptionHelpFormatter,
        description=config_description,
        help=config_description,
        epilog=config_example,
    )
    config_subparser = config_parser.add_subparsers()
    configure_vars_parser(config_subparser)