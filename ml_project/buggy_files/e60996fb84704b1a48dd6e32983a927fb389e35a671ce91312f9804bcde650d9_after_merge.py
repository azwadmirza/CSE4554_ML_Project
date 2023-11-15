def run(config, pid_file, daemon=False):
    delay = 20
    # Inject ca_certs from config to web for SSL validation of web requests
    if not config.core.ca_certs:
        tools.stderr(
            'Could not open CA certificates file. SSL will not work properly!')

    def signal_handler(sig, frame):
        if sig == signal.SIGUSR1 or sig == signal.SIGTERM or sig == signal.SIGINT:
            tools.stderr('Got quit signal, shutting down.')
            p.quit('Closing')
        elif sig == signal.SIGUSR2 or sig == signal.SIGILL:
            tools.stderr('Got restart signal.')
            p.restart('Restarting')

    # Define empty variable `p` for bot
    p = None
    while True:
        if p and p.hasquit:  # Check if `hasquit` was set for bot during disconnected phase
            break
        try:
            p = bot.Sopel(config, daemon=daemon)
            if hasattr(signal, 'SIGUSR1'):
                signal.signal(signal.SIGUSR1, signal_handler)
            if hasattr(signal, 'SIGTERM'):
                signal.signal(signal.SIGTERM, signal_handler)
            if hasattr(signal, 'SIGINT'):
                signal.signal(signal.SIGINT, signal_handler)
            if hasattr(signal, 'SIGUSR2'):
                signal.signal(signal.SIGUSR2, signal_handler)
            if hasattr(signal, 'SIGILL'):
                signal.signal(signal.SIGILL, signal_handler)
            logger.setup_logging(p)
            p.run(config.core.host, int(config.core.port))
        except KeyboardInterrupt:
            break
        except Exception:  # TODO: Be specific
            trace = traceback.format_exc()
            try:
                tools.stderr(trace)
            except Exception:  # TODO: Be specific
                pass
            logfile = open(os.path.join(config.core.logdir, 'exceptions.log'), 'a')
            logfile.write('Critical exception in core')
            logfile.write(trace)
            logfile.write('----------------------------------------\n\n')
            logfile.close()
            # TODO: This should be handled by command_start
            # All we should need here is a return value, but replacing the
            # os._exit() call below (at the end) broke ^C.
            # This one is much harder to test, so until that one's sorted it
            # isn't worth the risk of trying to remove this one.
            os.unlink(pid_file)
            os._exit(1)

        if not isinstance(delay, int):
            break
        if p.wantsrestart:
            return -1
        if p.hasquit:
            break
        tools.stderr(
            'Warning: Disconnected. Reconnecting in %s seconds...' % delay)
        time.sleep(delay)
    # TODO: This should be handled by command_start
    # All we should need here is a return value, but making this
    # a return makes Sopel hang on ^C after it says "Closed!"
    os.unlink(pid_file)
    os._exit(0)