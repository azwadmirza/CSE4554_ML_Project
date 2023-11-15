  def _format_unhandled_exception_log(cls, exc, tb, add_newline, should_print_backtrace):
    exc_type = type(exc)
    exception_full_name = '{}.{}'.format(exc_type.__module__, exc_type.__name__)
    exception_message = str(exc) if exc else '(no message)'
    maybe_newline = '\n' if add_newline else ''
    return cls._UNHANDLED_EXCEPTION_LOG_FORMAT.format(
      exception_type=exception_full_name,
      backtrace=cls._format_traceback(tb, should_print_backtrace=should_print_backtrace),
      exception_message=exception_message,
      maybe_newline=maybe_newline)