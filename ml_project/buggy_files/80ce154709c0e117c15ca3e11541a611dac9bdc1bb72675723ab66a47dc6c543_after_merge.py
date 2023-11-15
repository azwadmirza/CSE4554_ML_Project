def load_or_install_jrnl():
    """
    If jrnl is already installed, loads and returns a config object.
    Else, perform various prompts to install jrnl.
    """
    config_path = (
        get_config_path()
        if os.path.exists(get_config_path())
        else os.path.join(os.path.expanduser("~"), ".jrnl_config")
    )

    if os.path.exists(config_path):
        logging.debug("Reading configuration from file %s", config_path)
        config = load_config(config_path)

        if is_old_version(config_path):
            from . import upgrade

            try:
                upgrade.upgrade_jrnl(config_path)
            except upgrade.UpgradeValidationException:
                print("Aborting upgrade.", file=sys.stderr)
                print(
                    "Please tell us about this problem at the following URL:",
                    file=sys.stderr,
                )
                print(
                    "https://github.com/jrnl-org/jrnl/issues/new?title=UpgradeValidationException",
                    file=sys.stderr,
                )
                print("Exiting.", file=sys.stderr)
                sys.exit(1)

        upgrade_config(config)
        verify_config_colors(config)

    else:
        logging.debug("Configuration file not found, installing jrnl...")
        try:
            config = install()
        except KeyboardInterrupt:
            raise UserAbort("Installation aborted")

    logging.debug('Using configuration "%s"', config)
    return config