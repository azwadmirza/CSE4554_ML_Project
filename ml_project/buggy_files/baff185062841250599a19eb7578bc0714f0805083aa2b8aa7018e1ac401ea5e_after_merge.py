  def _exit_with_failure(cls, terminal_msg):
    formatted_terminal_msg = cls._EXIT_FAILURE_TERMINAL_MESSAGE_FORMAT.format(
      timestamp=cls._iso_timestamp_for_now(),
      terminal_msg=terminal_msg or '<no exit reason provided>')
    # Exit with failure, printing a message to the terminal (or whatever the interactive stream is).
    cls._exiter.exit_and_fail(msg=formatted_terminal_msg, out=cls._interactive_output_stream)