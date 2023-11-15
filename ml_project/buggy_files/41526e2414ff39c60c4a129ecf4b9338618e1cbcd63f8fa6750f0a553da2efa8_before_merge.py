def create_or_update_cluster(
        config_file: str, override_min_workers: Optional[int],
        override_max_workers: Optional[int], no_restart: bool,
        restart_only: bool, yes: bool, override_cluster_name: Optional[str],
        no_config_cache: bool, dump_command_output: bool,
        use_login_shells: bool) -> None:
    """Create or updates an autoscaling Ray cluster from a config json."""
    set_using_login_shells(use_login_shells)
    cmd_output_util.set_output_redirected(not dump_command_output)

    if use_login_shells:
        cli_logger.warning(
            "Commands running under a login shell can produce more "
            "output than special processing can handle.")
        cli_logger.warning(
            "Thus, the output from subcommands will be logged as is.")
        cli_logger.warning(
            "Consider using {}, {}.", cf.bold("--use-normal-shells"),
            cf.underlined("if you tested your workflow and it is compatible"))
        cli_logger.newline()

    cli_logger.detect_colors()

    def handle_yaml_error(e):
        cli_logger.error("Cluster config invalid\n")
        cli_logger.error("Failed to load YAML file " + cf.bold("{}"),
                         config_file)
        cli_logger.newline()
        with cli_logger.verbatim_error_ctx("PyYAML error:"):
            cli_logger.error(e)
        cli_logger.abort()

    try:
        config = yaml.safe_load(open(config_file).read())
    except FileNotFoundError:
        cli_logger.abort(
            "Provided cluster configuration file ({}) does not exist",
            cf.bold(config_file))
    except yaml.parser.ParserError as e:
        handle_yaml_error(e)
    except yaml.scanner.ScannerError as e:
        handle_yaml_error(e)

    # todo: validate file_mounts, ssh keys, etc.

    importer = NODE_PROVIDERS.get(config["provider"]["type"])
    if not importer:
        cli_logger.abort(
            "Unknown provider type " + cf.bold("{}") + "\n"
            "Available providers are: {}", config["provider"]["type"],
            cli_logger.render_list([
                k for k in NODE_PROVIDERS.keys()
                if NODE_PROVIDERS[k] is not None
            ]))
        raise NotImplementedError("Unsupported provider {}".format(
            config["provider"]))

    cli_logger.success("Cluster configuration valid\n")

    printed_overrides = False

    def handle_cli_override(key, override):
        if override is not None:
            if key in config:
                nonlocal printed_overrides
                printed_overrides = True
                cli_logger.warning(
                    "`{}` override provided on the command line.\n"
                    "  Using " + cf.bold("{}") + cf.dimmed(
                        " [configuration file has " + cf.bold("{}") + "]"),
                    key, override, config[key])
            config[key] = override

    handle_cli_override("min_workers", override_min_workers)
    handle_cli_override("max_workers", override_max_workers)
    handle_cli_override("cluster_name", override_cluster_name)

    if printed_overrides:
        cli_logger.newline()

    cli_logger.labeled_value("Cluster", config["cluster_name"])

    # disable the cli_logger here if needed
    # because it only supports aws
    if config["provider"]["type"] != "aws":
        cli_logger.old_style = True
    cli_logger.newline()
    config = _bootstrap_config(config, no_config_cache)
    if config["provider"]["type"] != "aws":
        cli_logger.old_style = False

    try_logging_config(config)
    get_or_create_head_node(config, config_file, no_restart, restart_only, yes,
                            override_cluster_name)