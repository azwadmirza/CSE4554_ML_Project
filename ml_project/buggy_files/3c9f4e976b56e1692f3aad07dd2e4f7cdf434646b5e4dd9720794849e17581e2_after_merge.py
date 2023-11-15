def start_tribler_core(base_path, api_port, api_key):
    """
    This method will start a new Tribler session.
    Note that there is no direct communication between the GUI process and the core: all communication is performed
    through the HTTP API.
    """
    from tribler_core.check_os import check_and_enable_code_tracing, set_process_priority, setup_core_logging
    setup_core_logging()

    from tribler_core.config.tribler_config import TriblerConfig
    from tribler_core.modules.process_checker import ProcessChecker
    from tribler_core.session import Session

    trace_logger = None

    def on_tribler_shutdown(future):
        future.result()
        get_event_loop().stop()
        if trace_logger:
            trace_logger.close()

    def shutdown(session, *_):
        logging.info("Stopping Tribler core")
        ensure_future(session.shutdown()).add_done_callback(on_tribler_shutdown)

    sys.path.insert(0, base_path)

    async def start_tribler():
        config = TriblerConfig()
        global trace_logger

        # Enable tracer if --trace-debug or --trace-exceptions flag is present in sys.argv
        trace_logger = check_and_enable_code_tracing('core')

        priority_order = config.get_cpu_priority_order()
        set_process_priority(pid=os.getpid(), priority_order=priority_order)

        config.set_http_api_port(int(api_port))
        # If the API key is set to an empty string, it will remain disabled
        if config.get_http_api_key() not in ('', api_key):
            config.set_http_api_key(api_key)
            config.write()  # Immediately write the API key so other applications can use it
        config.set_http_api_enabled(True)

        # Check if we are already running a Tribler instance
        process_checker = ProcessChecker(config.get_state_dir())
        if process_checker.already_running:
            return
        process_checker.create_lock_file()

        session = Session(config)

        signal.signal(signal.SIGTERM, lambda signum, stack: shutdown(session, signum, stack))
        await session.start()

    logging.getLogger('asyncio').setLevel(logging.WARNING)
    get_event_loop().create_task(start_tribler())
    get_event_loop().run_forever()