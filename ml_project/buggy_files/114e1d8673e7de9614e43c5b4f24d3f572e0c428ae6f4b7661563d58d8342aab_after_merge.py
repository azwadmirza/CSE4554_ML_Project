  def __init__(self, pre_obj=None):
    """Initialize the knowledge base object.

    Args:
        pre_obj: Optional preprocess object (instance of PreprocessObject.).
                 The default is None, which indicates the KnowledgeBase should
                 create a new PreprocessObject.
    """
    super(KnowledgeBase, self).__init__()

    # TODO: the first versions of the knowledge base will wrap the pre-process
    # object, but this should be replaced by an artifact style knowledge base
    # or artifact cache.
    if pre_obj:
      self._pre_obj = pre_obj
    else:
      self._pre_obj = event.PreprocessObject()

    self._default_codepage = u'cp1252'
    self._default_timezone = pytz.timezone(u'UTC')