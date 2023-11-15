  def reset_log_location(cls, new_log_location):
    """Re-acquire file handles to error logs based in the new location.

    Class state:
    - Overwrites `cls._log_dir`, `cls._pid_specific_error_fileobj`, and
      `cls._shared_error_fileobj`.
    OS state:
    - May create a new directory.
    - Overwrites signal handlers for many fatal and non-fatal signals.

    :raises: :class:`ExceptionSink.ExceptionSinkError` if the directory does not exist or is not
             writable.
    """
    # We could no-op here if the log locations are the same, but there's no reason not to have the
    # additional safety of re-acquiring file descriptors each time (and erroring out early if the
    # location is no longer writable).

    # Create the directory if possible, or raise if not writable.
    cls._check_or_create_new_destination(new_log_location)

    pid_specific_error_stream, shared_error_stream = cls._recapture_fatal_error_log_streams(
      new_log_location)

    # NB: mutate process-global state!
    if faulthandler.is_enabled():
      logger.debug('re-enabling faulthandler')
      # Call Py_CLEAR() on the previous error stream:
      # https://github.com/vstinner/faulthandler/blob/master/faulthandler.c
      faulthandler.disable()
    # Send a stacktrace to this file if interrupted by a fatal error.
    faulthandler.enable(file=pid_specific_error_stream, all_threads=True)

    # NB: mutate the class variables!
    cls._log_dir = new_log_location
    cls._pid_specific_error_fileobj = pid_specific_error_stream
    cls._shared_error_fileobj = shared_error_stream