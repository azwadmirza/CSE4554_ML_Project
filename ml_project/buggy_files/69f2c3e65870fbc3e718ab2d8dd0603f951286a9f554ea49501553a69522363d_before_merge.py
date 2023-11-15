  def __init__(self, analyzer_class):
    """Initializes a hash tagging analysis plugin.

    Args:
      analyzer_class (type): A subclass of HashAnalyzer that will be
          instantiated by the plugin.
    """
    super(HashTaggingAnalysisPlugin, self).__init__()
    self._analysis_queue_timeout = self.DEFAULT_QUEUE_TIMEOUT
    self._analyzer_started = False
    self._event_uuids_by_pathspec = defaultdict(list)
    self._hash_pathspecs = defaultdict(list)
    self._requester_class = None
    self._time_of_last_status_log = time.time()
    self.hash_analysis_queue = Queue.Queue()
    self.hash_queue = Queue.Queue()

    self._analyzer = analyzer_class(self.hash_queue, self.hash_analysis_queue)