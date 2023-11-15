  def _format_traceback(cls, tb, should_print_backtrace):
    if should_print_backtrace:
      traceback_string = '\n{}'.format(''.join(traceback.format_tb(tb)))
    else:
      traceback_string = ' {}'.format(cls._traceback_omitted_default_text)
    return traceback_string