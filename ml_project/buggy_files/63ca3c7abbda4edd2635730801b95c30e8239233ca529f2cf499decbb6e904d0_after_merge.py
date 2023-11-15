def _add_install(subparsers):
    p = subparsers.add_parser(
        "install",
        help="Install a package",
        formatter_class=LineWrapRawTextHelpFormatter,
        description=INSTALL_DESCRIPTION,
    )
    p.add_argument("package", help="package name")
    p.add_argument("--spec", help=SPEC_HELP)
    add_include_dependencies(p)
    p.add_argument("--verbose", action="store_true")
    p.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Modify existing virtual environment and files in PIPX_BIN_DIR",
    )
    p.add_argument(
        "--python",
        default=constants.DEFAULT_PYTHON,
        help=(
            "The Python executable used to create the Virtual Environment and run the "
            "associated app/apps. Must be v3.5+."
        ),
    )
    add_pip_venv_args(p)