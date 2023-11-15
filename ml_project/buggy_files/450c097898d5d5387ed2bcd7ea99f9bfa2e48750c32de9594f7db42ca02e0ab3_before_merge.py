  def EnableFreeAPIKeyRateLimit(self, rate_limit):
    """Configures Rate limiting for queries to VirusTotal.

    The default rate limit for free VirusTotal API keys is 4 requests per
    minute.

    Args:
      rate_limit (bool): whether to apply the free API key rate limit.
    """
    if rate_limit:
      self._analyzer.hashes_per_batch = 4
      self._analyzer.wait_after_analysis = 60
      self._analysis_queue_timeout = self._analyzer.wait_after_analysis + 1