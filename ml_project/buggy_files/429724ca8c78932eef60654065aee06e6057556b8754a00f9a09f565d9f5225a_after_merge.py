def main(args):
    setup_reporter(args)
    try:
        config = load_config(args)
        config.logdir.ensure(dir=1)
        ensure_empty_dir(config.logdir)
        with set_os_env_var("TOX_WORK_DIR", config.toxworkdir):
            session = build_session(config)
            exit_code = session.runcommand()
        if exit_code is None:
            exit_code = 0
        raise SystemExit(exit_code)
    except tox.exception.BadRequirement:
        raise SystemExit(1)
    except KeyboardInterrupt:
        raise SystemExit(2)