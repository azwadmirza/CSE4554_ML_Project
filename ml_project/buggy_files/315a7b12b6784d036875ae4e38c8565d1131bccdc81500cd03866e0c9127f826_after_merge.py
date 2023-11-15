def make_stderr_observer(levels=(LogLevel.warn, LogLevel.error,
                                 LogLevel.critical),
                         show_source=False, format="standard",
                         colour=False, _file=None, _categories=None):
    """
    Create an observer which prints logs to L{sys.stderr}.
    """
    if _file is None:
        _file = sys.__stderr__

    if _categories is None:
        from crossbar._log_categories import log_categories as _categories

    @provider(ILogObserver)
    def StandardErrorObserver(event):

        if event["log_level"] not in levels:
            return

        if event.get("log_system", u"-") == u"-":
            logSystem = u"{:<10} {:>6}".format("Controller", os.getpid())
        else:
            logSystem = event["log_system"]

        if show_source and event.get("log_namespace") is not None:
            logSystem += " " + event.get("cb_namespace", event.get("log_namespace", ''))

        if event.get("log_category"):
            format_string = _categories.get(event['log_category'])
            if format_string:
                event = event.copy()
                event["log_format"] = format_string

        if event.get("log_format", None) is not None:
            eventText = formatEvent(event)
        else:
            eventText = u""

        if "log_failure" in event:
            # This is a traceback. Print it.
            eventText = eventText + event["log_failure"].getTraceback()

        if format == "standard":
            FORMAT_STRING = STANDARD_FORMAT
        elif format == "syslogd":
            FORMAT_STRING = SYSLOGD_FORMAT
        elif format == "none":
            FORMAT_STRING = NONE_FORMAT
        else:
            assert False

        if colour:
            # Errors are always red.
            fore = Fore.RED

            eventString = FORMAT_STRING.format(
                startcolour=fore, time=formatTime(event["log_time"]),
                system=logSystem, endcolour=Fore.RESET,
                text=eventText)
        else:
            eventString = strip_ansi(FORMAT_STRING.format(
                startcolour=u'', time=formatTime(event["log_time"]),
                system=logSystem, endcolour=u'',
                text=eventText))

        print(eventString, file=_file)

    return StandardErrorObserver