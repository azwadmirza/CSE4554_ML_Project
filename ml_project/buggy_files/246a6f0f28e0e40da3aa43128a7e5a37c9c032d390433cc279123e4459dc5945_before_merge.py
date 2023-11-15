def tox_add_option(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--no-recreate-provision",
        dest="recreate",
        help="if recreate is set do not recreate provision tox environment",
        action="store_true",
    )