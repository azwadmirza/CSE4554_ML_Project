  def __init__(self):
    """Initialize the knowledge base object."""
    super(KnowledgeBase, self).__init__()

    # TODO: the first versions of the knowledge base will wrap the pre-process
    # object, but this should be replaced by an artifact style knowledge base
    # or artifact cache.
    self._pre_obj = event.PreprocessObject()

    self._default_codepage = u'cp1252'
    self._default_timezone = pytz.timezone(u'UTC')