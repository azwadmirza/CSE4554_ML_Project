  def reset_interactive_output_stream(cls, interactive_output_stream):
    """
    Class state:
    - Overwrites `cls._interactive_output_stream`.
    OS state:
    - Overwrites the SIGUSR2 handler.

    This method registers a SIGUSR2 handler, which permits a non-fatal `kill -31 <pants pid>` for
    stacktrace retrieval. This is also where the the error message on fatal exit will be printed to.
    """
    try:
      # NB: mutate process-global state!
      # This permits a non-fatal `kill -31 <pants pid>` for stacktrace retrieval.
      faulthandler.register(signal.SIGUSR2, interactive_output_stream,
                            all_threads=True, chain=False)
      # NB: mutate the class variables!
      cls._interactive_output_stream = interactive_output_stream
    except ValueError:
      # Warn about "ValueError: IO on closed file" when the stream is closed.
      cls.log_exception(
        "Cannot reset interactive_output_stream -- stream (probably stderr) is closed")