def signal_handler(handler):
    _thread_local = threading.local()
    _thread_local.previous_handlers = []
    for signame in INTERRUPT_SIGNALS:
        sig = getattr(signal, signame, None)
        if sig:
            log.debug("registering handler for %s", signame)
            try:
                prev_handler = signal.signal(sig, handler)
                _thread_local.previous_handlers.append((sig, prev_handler))
            except ValueError as e:
                # ValueError: signal only works in main thread
                log.debug('%r', e)
    try:
        yield
    finally:
        standard_handlers = signal.SIG_IGN, signal.SIG_DFL
        for sig, previous_handler in _thread_local.previous_handlers:
            if callable(previous_handler) or previous_handler in standard_handlers:
                log.debug("de-registering handler for %s", sig)
                signal.signal(sig, previous_handler)