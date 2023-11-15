def show_config(config):
    parser = configparser.ConfigParser()

    if not config.envlist_explicit or reporter.verbosity() >= reporter.Verbosity.INFO:
        tox_info(config, parser)
        version_info(parser)
    tox_envs_info(config, parser)

    content = StringIO()
    parser.write(content)
    value = content.getvalue().rstrip()
    reporter.verbosity0(value)