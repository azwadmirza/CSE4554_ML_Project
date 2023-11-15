  def __init__(
      self, output_mediator, host, port, flush_interval, index_name, mapping,
      doc_type, elastic_user, elastic_password):
    """Create a Elasticsearch helper.

    Args:
      output_mediator (OutputMediator): The output mediator object.
      host (str): IP address or hostname for the server.
      port (int): Port number for the server.
      flush_interval (int): How many events to queue before being indexed.
      index_name (str): Name of the Elasticsearch index.
      mapping (dict): Elasticsearch index configuration.
      doc_type (str): Elasticsearch document type name.
      elastic_user (str): Elasticsearch username to authenticate with.
      elastic_passsword (str): Elasticsearch password to authenticate with
    """
    super(ElasticSearchHelper, self).__init__()
    if elastic_user is None:
      self.client = Elasticsearch([{u'host': host, u'port': port}])
    else:
      self.client = Elasticsearch([{u'host': host, u'port': port}],
                                  http_auth=(elastic_user, elastic_password))
    self._output_mediator = output_mediator
    self._index = self._EnsureIndexExists(index_name, mapping)
    self._doc_type = doc_type
    self._flush_interval = flush_interval
    self._events = []
    self._counter = Counter()
    self._elastic_user = elastic_user
    self._elastic_password = elastic_password