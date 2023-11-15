  def Analyze(self, hashes):
    """Looks up hashes in Viper using the Viper HTTP API.

    The API is documented here:
      https://viper-framework.readthedocs.org/en/latest/usage/web.html#api

    Args:
      hashes: A list of hashes (strings) to look up. The Viper plugin supports
              only one hash at a time.

    Returns:
      A list of hash analysis objects (instances of HashAnalysis).

    Raises:
      RuntimeError: If no host has been set for Viper.
      ValueError: If the hashes list contains a number of hashes other than
                      one.
    """
    if not self._host:
      raise RuntimeError(u'No host specified for Viper lookup.')

    if len(hashes) != 1:
      raise ValueError(
          u'Unsupported number of hashes provided. Viper supports only one '
          u'hash at a time.')
    sha256 = hashes[0]

    hash_analyses = []
    url = u'{0:s}://{1:s}:{2:d}/{3:s}'.format(
        self._protocol, self._host, self._port, self._VIPER_API_PATH)
    params = {u'sha256': sha256}
    try:
      json_response = self.MakeRequestAndDecodeJSON(url, u'POST', data=params)
    except errors.ConnectionError as exception:
      logging.error(
          (u'Error communicating with Viper {0:s}. Viper plugin is '
           u'aborting.').format(exception))
      self.SignalAbort()
      return hash_analyses

    hash_analysis = interface.HashAnalysis(sha256, json_response)
    hash_analyses.append(hash_analysis)
    return hash_analyses