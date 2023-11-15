def run():
    global args
    args = parse_args()
    if args.stop:
        stop_daemon(args)
        sys.exit(0)

    if args.respawn:
        stop_daemon(args)
        time.sleep(3)

    install_example_config_file()

    os.makedirs(args.run_dir, exist_ok=True)
    daemon = Daemonize(app="openrazer-daemon",
                       pid=os.path.join(args.run_dir, "openrazer-daemon.pid"),
                       action=run_daemon,
                       foreground=args.foreground,
                       verbose=args.verbose,
                       chdir=args.run_dir)
    daemon.start()