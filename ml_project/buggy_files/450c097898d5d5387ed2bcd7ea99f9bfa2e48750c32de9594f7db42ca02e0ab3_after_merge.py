  def EnableFreeAPIKeyRateLimit(self):
    """Configures Rate limiting for queries to VirusTotal.

    The default rate limit for free VirusTotal API keys is 4 requests per
    minute.
    """
    self._analyzer.hashes_per_batch = 4
    self._analyzer.wait_after_analysis = 60
    self._analysis_queue_timeout = self._analyzer.wait_after_analysis + 1