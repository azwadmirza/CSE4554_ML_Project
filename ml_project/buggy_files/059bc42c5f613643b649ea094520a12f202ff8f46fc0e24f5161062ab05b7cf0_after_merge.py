def upgrade_config(config):
    """Checks if there are keys missing in a given config dict, and if so, updates the config file accordingly.
    This essentially automatically ports jrnl installations if new config parameters are introduced in later
    versions."""
    default_config = get_default_config()
    missing_keys = set(default_config).difference(config)
    if missing_keys:
        for key in missing_keys:
            config[key] = default_config[key]
        save_config(config)
        print(
            f"[Configuration updated to newest version at {get_config_path()}]",
            file=sys.stderr,
        )