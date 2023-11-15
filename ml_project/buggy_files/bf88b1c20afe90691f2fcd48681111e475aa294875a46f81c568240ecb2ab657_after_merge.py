  def _format_traceback(cls, traceback_lines, should_print_backtrace):
    if should_print_backtrace:
      traceback_string = '\n{}'.format(''.join(traceback_lines))
    else:
      traceback_string = ' {}'.format(cls._traceback_omitted_default_text)
    return traceback_string