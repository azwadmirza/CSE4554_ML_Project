def configure_parser(sub_parsers):
    list_parser = sub_parsers.add_parser(
        'list',
        formatter_class=RawDescriptionHelpFormatter,
        description=description,
        help=description,
        epilog=example,
    )

    common.add_parser_json(list_parser)

    list_parser.set_defaults(func=execute)