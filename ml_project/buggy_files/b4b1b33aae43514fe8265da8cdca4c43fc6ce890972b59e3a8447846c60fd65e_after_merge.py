def run():
    global args

    logger = None
    args = parse_args()

    if args.stop:
        stop_daemon(args)
        sys.exit(0)

    if args.respawn:
        stop_daemon(args)
        time.sleep(3)

    # daemonize logs exceptions to its logger (which defaults to the syslog)
    # and does not make them appear on stdout/stderr. If we're in foreground
    # mode, override that logger with our own.
    if not args.foreground:
        logger = logging.getLogger('run-daemon')
        if args.verbose:
            logger.setLevel(logging.DEBUG)

    install_example_config_file()

    os.makedirs(args.run_dir, exist_ok=True)
    daemon = Daemonize(app="openrazer-daemon",
                       pid=os.path.join(args.run_dir, "openrazer-daemon.pid"),
                       action=run_daemon,
                       foreground=args.foreground,
                       verbose=args.verbose,
                       chdir=args.run_dir,
                       logger=logger)
    daemon.start()