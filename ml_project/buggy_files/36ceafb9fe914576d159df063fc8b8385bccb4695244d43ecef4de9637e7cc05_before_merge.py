  def __init__(self, output_mediator):
    """Initializes the output module object.

    Args:
      output_mediator: The output mediator object (instance of OutputMediator).
    """
    super(ElasticSearchOutputModule, self).__init__(output_mediator)

    self._doc_type = None
    self._elastic = None
    self._flush_interval = None
    self._host = None
    self._index_name = None
    self._mapping = None
    self._output_mediator = output_mediator
    self._port = None
    self._raw_fields = False
    self._elastic_user = None
    self._elastic_password = None