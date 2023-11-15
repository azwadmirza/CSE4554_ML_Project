def log_signals(obj):
    """Log all signals of an object or class.

    Can be used as class decorator.
    """
    def log_slot(obj, signal, *args):
        """Slot connected to a signal to log it."""
        dbg = dbg_signal(signal, args)
        try:
            r = repr(obj)
        except RuntimeError:  # pragma: no cover
            r = '<deleted>'
        log.signals.debug("Signal in {}: {}".format(r, dbg))

    def connect_log_slot(obj):
        """Helper function to connect all signals to a logging slot."""
        metaobj = obj.metaObject()
        for i in range(metaobj.methodCount()):
            meta_method = metaobj.method(i)
            qtutils.ensure_valid(meta_method)
            if meta_method.methodType() == QMetaMethod.Signal:
                name = bytes(meta_method.name()).decode('ascii')
                if name != 'destroyed':
                    signal = getattr(obj, name)
                    try:
                        signal.connect(functools.partial(
                            log_slot, obj, signal))
                    except TypeError:  # pragma: no cover
                        pass

    if inspect.isclass(obj):
        old_init = obj.__init__

        @functools.wraps(old_init)
        def new_init(self, *args, **kwargs):
            """Wrapper for __init__() which logs signals."""
            ret = old_init(self, *args, **kwargs)
            connect_log_slot(self)
            return ret

        obj.__init__ = new_init
    else:
        connect_log_slot(obj)

    return obj