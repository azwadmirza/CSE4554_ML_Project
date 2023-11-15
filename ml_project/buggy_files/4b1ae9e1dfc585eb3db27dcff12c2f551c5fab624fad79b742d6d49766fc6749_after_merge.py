    def start_tribler():
        config = TriblerConfig()

        if sys.platform == "darwin":
            # Due to a bug when using the keyring from a forked subprocess on MacOS, we have to patch these methods.
            patch_wallet_methods()
            patch_iom_methods()

        config.set_http_api_port(api_port)
        config.set_http_api_enabled(True)

        # Check if we are already running a Tribler instance
        process_checker = ProcessChecker(config.get_state_dir())
        if process_checker.already_running:
            return
        else:
            process_checker.create_lock_file()

        session = Session(config)

        signal.signal(signal.SIGTERM, lambda signum, stack: shutdown(session, signum, stack))
        session.start()