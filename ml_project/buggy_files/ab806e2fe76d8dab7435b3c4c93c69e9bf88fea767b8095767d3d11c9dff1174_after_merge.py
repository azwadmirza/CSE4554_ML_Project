  def __init__(self, message='', exit_code=PANTS_FAILED_EXIT_CODE):
    """
    :param int exit_code: an optional exit code (defaults to PANTS_FAILED_EXIT_CODE)
    """
    super(GracefulTerminationException, self).__init__(message)

    if exit_code == PANTS_SUCCEEDED_EXIT_CODE:
      raise ValueError(
        "Cannot create GracefulTerminationException with a successful exit code of {}"
        .format(PANTS_SUCCEEDED_EXIT_CODE))

    self._exit_code = exit_code