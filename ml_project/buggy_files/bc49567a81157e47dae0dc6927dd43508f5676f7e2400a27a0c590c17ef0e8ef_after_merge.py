  def __init__(self, *args, **kwargs):
    """
    :param int exit_code: an optional exit code (defaults to nonzero)
    :param list failed_targets: an optional list of failed targets (default=[])
    """
    self._exit_code = kwargs.pop('exit_code', PANTS_FAILED_EXIT_CODE)
    self._failed_targets = kwargs.pop('failed_targets', [])
    super(TaskError, self).__init__(*args, **kwargs)