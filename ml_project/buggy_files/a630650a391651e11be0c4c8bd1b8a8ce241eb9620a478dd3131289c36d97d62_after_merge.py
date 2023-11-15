def run_main(workdir, config_file=None, fc_dir=None, run_info_yaml=None,
             parallel=None, workflow=None):
    """Run variant analysis, handling command line options.
    """
    # Set environment to standard to use periods for decimals and avoid localization
    locale_to_use = utils.get_locale()
    os.environ["LC_ALL"] = locale_to_use
    os.environ["LC"] = locale_to_use
    os.environ["LANG"] = locale_to_use
    workdir = utils.safe_makedir(os.path.abspath(workdir))
    os.chdir(workdir)
    config, config_file = config_utils.load_system_config(config_file, workdir)
    log.setup_local_logging(config, parallel)
    logger.info(f"System YAML configuration: {os.path.abspath(config_file)}.")
    logger.info(f"Locale set to {locale_to_use}.")
    if config.get("log_dir", None) is None:
        config["log_dir"] = os.path.join(workdir, DEFAULT_LOG_DIR)
    if parallel["type"] in ["local", "clusterk"]:
        _setup_resources()
        _run_toplevel(config, config_file, workdir, parallel,
                      fc_dir, run_info_yaml)
    elif parallel["type"] == "ipython":
        assert parallel["scheduler"] is not None, "IPython parallel requires a specified scheduler (-s)"
        if parallel["scheduler"] != "sge":
            assert parallel["queue"] is not None, "IPython parallel requires a specified queue (-q)"
        elif not parallel["queue"]:
            parallel["queue"] = ""
        _run_toplevel(config, config_file, workdir, parallel,
                      fc_dir, run_info_yaml)
    else:
        raise ValueError("Unexpected type of parallel run: %s" % parallel["type"])