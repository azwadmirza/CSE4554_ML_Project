def handle_exception(exc_type, exception, traceback, hook=sys.excepthook):
    if environments.is_verbose() or not issubclass(exc_type, ClickException):
        hook(exc_type, exception, traceback)
    else:
        exc = format_exception(exc_type, exception, traceback)
        tb = format_tb(traceback, limit=-6)
        lines = itertools.chain.from_iterable([frame.splitlines() for frame in tb])
        for line in lines:
            line = line.strip("'").strip('"').strip("\n").strip()
            if not line.startswith("File"):
                line = "      {0}".format(line)
            else:
                line = "  {0}".format(line)
            line = "[pipenv.exceptions.{0!s}]: {1}".format(
                exception.__class__.__name__, line
            )
            click_echo(fix_utf8(line), err=True)
        exception.show()