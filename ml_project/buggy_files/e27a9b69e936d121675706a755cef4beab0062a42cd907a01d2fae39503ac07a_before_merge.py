  def __init__(self, hash_queue, hash_analysis_queue, **kwargs):
    """Initializes a Viper hash analyzer.

    Args:
      hash_queue: A queue (instance of Queue.queue) that contains hashes to
                  be analyzed.
      hash_analysis_queue: A queue (instance of Queue.queue) that the analyzer
                           will append HashAnalysis objects to.
    """
    super(ViperAnalyzer, self).__init__(
        hash_queue, hash_analysis_queue, **kwargs)
    self._checked_for_old_python_version = False
    self._host = None
    self._protocol = None