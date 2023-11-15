  def __init__(self, output_mediator):
    """Initializes the output module object.

    Args:
      output_mediator: The output mediator object (instance of OutputMediator).
    """
    super(PlasoStorageOutputModule, self).__init__(output_mediator)
    self._file_object = None
    self._storage = None