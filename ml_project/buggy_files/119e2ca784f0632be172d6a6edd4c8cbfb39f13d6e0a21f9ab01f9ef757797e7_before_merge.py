def list_journals(config):
    from . import install

    """List the journals specified in the configuration file"""
    result = f"Journals defined in {install.CONFIG_FILE_PATH}\n"
    ml = min(max(len(k) for k in config["journals"]), 20)
    for journal, cfg in config["journals"].items():
        result += " * {:{}} -> {}\n".format(
            journal, ml, cfg["journal"] if isinstance(cfg, dict) else cfg
        )
    return result