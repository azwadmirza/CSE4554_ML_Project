  def exit(self, result=PANTS_SUCCEEDED_EXIT_CODE, msg=None, out=None):
    """Exits the runtime.

    :param result: The exit status. Typically either PANTS_SUCCEEDED_EXIT_CODE or
                   PANTS_FAILED_EXIT_CODE, but can be a string as well. (Optional)
    :param msg: A string message to print to stderr or another custom file desciptor before exiting.
                (Optional)
    :param out: The file descriptor to emit `msg` to. (Optional)
    """
    if msg:
      out = out or sys.stderr
      if PY3 and hasattr(out, 'buffer'):
        out = out.buffer

      msg = ensure_binary(msg)
      try:
        out.write(msg)
        out.write(b'\n')
        # TODO: Determine whether this call is a no-op because the stream gets flushed on exit, or
        # if we could lose what we just printed, e.g. if we get interrupted by a signal while
        # exiting and the stream is buffered like stdout.
        out.flush()
      except Exception as e:
        # If the file is already closed, or any other error occurs, just log it and continue to
        # exit.
        logger.exception(e)
    self._exit(result)