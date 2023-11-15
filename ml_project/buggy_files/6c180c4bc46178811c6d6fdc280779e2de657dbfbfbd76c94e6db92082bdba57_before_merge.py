def signal_handler(handler):
    previous_handlers = []
    for signame in INTERRUPT_SIGNALS:
        sig = getattr(signal, signame, None)
        if sig:
            log.debug("registering handler for %s", signame)
            prev_handler = signal.signal(sig, handler)
            previous_handlers.append((sig, prev_handler))
    try:
        yield
    finally:
        standard_handlers = signal.SIG_IGN, signal.SIG_DFL
        for sig, previous_handler in previous_handlers:
            if callable(previous_handler) or previous_handler in standard_handlers:
                log.debug("de-registering handler for %s", sig)
                signal.signal(sig, previous_handler)