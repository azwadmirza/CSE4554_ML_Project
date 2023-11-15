def start(hs: "synapse.server.HomeServer", listeners: Iterable[ListenerConfig]):
    """
    Start a Synapse server or worker.

    Should be called once the reactor is running and (if we're using ACME) the
    TLS certificates are in place.

    Will start the main HTTP listeners and do some other startup tasks, and then
    notify systemd.

    Args:
        hs: homeserver instance
        listeners: Listener configuration ('listeners' in homeserver.yaml)
    """
    try:
        # Set up the SIGHUP machinery.
        if hasattr(signal, "SIGHUP"):

            def handle_sighup(*args, **kwargs):
                # Tell systemd our state, if we're using it. This will silently fail if
                # we're not using systemd.
                sdnotify(b"RELOADING=1")

                for i, args, kwargs in _sighup_callbacks:
                    i(*args, **kwargs)

                sdnotify(b"READY=1")

            signal.signal(signal.SIGHUP, handle_sighup)

            register_sighup(refresh_certificate, hs)

        # Load the certificate from disk.
        refresh_certificate(hs)

        # Start the tracer
        synapse.logging.opentracing.init_tracer(  # type: ignore[attr-defined] # noqa
            hs
        )

        # It is now safe to start your Synapse.
        hs.start_listening(listeners)
        hs.get_datastore().db_pool.start_profiling()
        hs.get_pusherpool().start()

        # Log when we start the shut down process.
        hs.get_reactor().addSystemEventTrigger(
            "before", "shutdown", logger.info, "Shutting down..."
        )

        setup_sentry(hs)
        setup_sdnotify(hs)

        # If background tasks are running on the main process, start collecting the
        # phone home stats.
        if hs.config.run_background_tasks:
            start_phone_stats_home(hs)

        # We now freeze all allocated objects in the hopes that (almost)
        # everything currently allocated are things that will be used for the
        # rest of time. Doing so means less work each GC (hopefully).
        #
        # This only works on Python 3.7
        if sys.version_info >= (3, 7):
            gc.collect()
            gc.freeze()
    except Exception:
        traceback.print_exc(file=sys.stderr)
        reactor = hs.get_reactor()
        if reactor.running:
            reactor.stop()
        sys.exit(1)