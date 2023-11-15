def main():
    original_argv = list(sys.argv)
    try:
        parse_argv()
    except Exception as exc:
        print(str(HELP) + str("\nError: ") + str(exc), file=sys.stderr)
        sys.exit(2)

    if options.log_to is not None:
        debugpy.log_to(options.log_to)
    if options.log_to_stderr:
        debugpy.log_to(sys.stderr)

    api.ensure_logging()

    log.info(
        str("sys.argv before parsing: {0!r}\n" "         after parsing:  {1!r}"),
        original_argv,
        sys.argv,
    )

    try:
        run = {
            "file": run_file,
            "module": run_module,
            "code": run_code,
            "pid": attach_to_pid,
        }[options.target_kind]
        run()
    except SystemExit as exc:
        log.reraise_exception(
            "Debuggee exited via SystemExit: {0!r}", exc.code, level="debug"
        )