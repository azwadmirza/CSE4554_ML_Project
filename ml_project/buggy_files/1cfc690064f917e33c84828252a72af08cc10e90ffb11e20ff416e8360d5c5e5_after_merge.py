    async def start_tribler():
        # Check if we are already running a Tribler instance
        process_checker = ProcessChecker(root_state_dir)
        if process_checker.already_running:
            return
        process_checker.create_lock_file()

        # Before any upgrade, prepare a separate state directory for the update version so it does not
        # affect the older version state directory. This allows for safe rollback.
        fork_state_directory_if_necessary(root_state_dir, version_id)

        state_dir = get_versioned_state_directory(root_state_dir)

        config = TriblerConfig(state_dir, config_file=state_dir / CONFIG_FILENAME, reset_config_on_error=True)

        if not config.get_core_error_reporting_requires_user_consent():
            SentryReporter.global_strategy = SentryStrategy.SEND_ALLOWED

        config.set_api_http_port(int(api_port))
        # If the API key is set to an empty string, it will remain disabled
        if config.get_api_key() not in ('', api_key):
            config.set_api_key(api_key)
            config.write()  # Immediately write the API key so other applications can use it
        config.set_api_http_enabled(True)

        priority_order = config.get_cpu_priority_order()
        set_process_priority(pid=os.getpid(), priority_order=priority_order)

        global trace_logger
        # Enable tracer if --trace-debug or --trace-exceptions flag is present in sys.argv
        trace_logger = check_and_enable_code_tracing('core', config.get_log_dir())

        session = Session(config, core_test_mode=core_test_mode)

        signal.signal(signal.SIGTERM, lambda signum, stack: shutdown(session, signum, stack))
        await session.start()