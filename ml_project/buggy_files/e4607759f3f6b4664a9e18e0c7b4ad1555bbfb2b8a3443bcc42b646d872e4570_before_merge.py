  def GetResults(self):
    """Retrieves the hashing results.

    Returns:
      list[AnalyzerResult]: results.
    """
    results = []
    for hasher in self._hashers:
      logging.debug(u'Processing results for hasher {0:s}'.format(hasher))
      result = analyzer_result.AnalyzerResult()
      result.analyzer_name = self.NAME
      result.attribute_name = u'{0:s}_hash'.format(hasher.NAME)
      result.attribute_value = hasher.GetStringDigest()
      results.append(result)
    return results