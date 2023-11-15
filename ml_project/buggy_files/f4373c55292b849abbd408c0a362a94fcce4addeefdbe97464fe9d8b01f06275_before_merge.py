def configure_parser(sub_parsers):
    l = sub_parsers.add_parser(
        'list',
        formatter_class=RawDescriptionHelpFormatter,
        description=description,
        help=description,
        epilog=example,
    )

    common.add_parser_json(l)

    l.set_defaults(func=execute)