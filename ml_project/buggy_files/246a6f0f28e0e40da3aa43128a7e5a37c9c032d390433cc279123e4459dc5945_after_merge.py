def tox_add_option(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--no-recreate-provision",
        dest="no_recreate_provision",
        help="if recreate is set do not recreate provision tox environment",
        action="store_true",
    )
    parser.add_argument(
        "-r",
        "--recreate",
        dest="recreate",
        help="recreate the tox environments",
        action="store_true",
    )