  def __init__(self, message='', exit_code=1):
    """
    :param int exit_code: an optional exit code (default=1)
    """
    super(GracefulTerminationException, self).__init__(message)

    if exit_code == 0:
      raise ValueError("Cannot create GracefulTerminationException with exit code of 0")

    self._exit_code = exit_code