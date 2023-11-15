  def reset_interactive_output_stream(cls, interactive_output_stream):
    """
    Class state:
    - Overwrites `cls._interactive_output_stream`.
    OS state:
    - Overwrites the SIGUSR2 handler.

    This is where the the error message on exit will be printed to as well.
    """
    try:
      # NB: mutate process-global state!
      if faulthandler.unregister(signal.SIGUSR2):
        logger.debug('re-registering a SIGUSR2 handler')
      # This permits a non-fatal `kill -31 <pants pid>` for stacktrace retrieval.
      faulthandler.register(signal.SIGUSR2, interactive_output_stream,
                            all_threads=True, chain=False)

      # NB: mutate the class variables!
      # We don't *necessarily* need to keep a reference to this, but we do here for clarity.
      cls._interactive_output_stream = interactive_output_stream
    except ValueError:
      # Warn about "ValueError: IO on closed file" when stderr is closed.
      ExceptionSink.log_exception("Cannot reset output stream - sys.stderr is closed")