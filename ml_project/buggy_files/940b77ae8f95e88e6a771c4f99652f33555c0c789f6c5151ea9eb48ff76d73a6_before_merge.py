    def debug(address, **kwargs):
        if _settrace.called:
            raise RuntimeError("this process already has a debug adapter")

        try:
            _, port = address
        except Exception:
            port = address
            address = ("127.0.0.1", port)
        try:
            port.__index__()  # ensure it's int-like
        except Exception:
            raise ValueError("expected port or (host, port)")
        if not (0 <= port < 2 ** 16):
            raise ValueError("invalid port number")

        ensure_logging()
        log.debug("{0}({1!r}, **{2!r})", func.__name__, address, kwargs)
        log.info("Initial debug configuration: {0!j}", _config)

        qt_mode = _config.get("qt", "none")
        if qt_mode != "none":
            pydevd.enable_qt_support(qt_mode)

        settrace_kwargs = {
            "suspend": False,
            "patch_multiprocessing": _config.get("subProcess", True),
        }

        debugpy_path = os.path.dirname(absolute_path(debugpy.__file__))
        settrace_kwargs["dont_trace_start_patterns"] = (debugpy_path,)
        settrace_kwargs["dont_trace_end_patterns"] = ("debugpy_launcher.py",)

        try:
            return func(address, settrace_kwargs, **kwargs)
        except Exception:
            log.reraise_exception("{0}() failed:", func.__name__, level="info")