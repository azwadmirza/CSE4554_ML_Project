def run(args=None, options=None):
    start = datetime.now()
    from virtualenv.error import ProcessCallFailed
    from virtualenv.run import cli_run

    if args is None:
        args = sys.argv[1:]
    try:
        session = cli_run(args, options)
        logging.warning(LogSession(session, start))
    except ProcessCallFailed as exception:
        print("subprocess call failed for {} with code {}".format(exception.cmd, exception.code))
        print(exception.out, file=sys.stdout, end="")
        print(exception.err, file=sys.stderr, end="")
        raise SystemExit(exception.code)