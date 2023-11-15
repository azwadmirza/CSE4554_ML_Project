  def Analyze(self, hashes):
    """Looks up hashes in nsrlsvr.

    Args:
      hashes (list[str]): hash values to look up.

    Returns:
      list[HashAnalysis]: analysis results, or an empty list on error.
    """
    logging.debug(
        u'Opening connection to {0:s}:{1:d}'.format(self._host, self._port))

    nsrl_socket = self._GetSocket()
    if not nsrl_socket:
      self.SignalAbort()
      return []

    hash_analyses = []
    for digest in hashes:
      response = self._QueryHash(nsrl_socket, digest)
      if response is None:
        continue

      hash_analysis = interface.HashAnalysis(digest, response)
      hash_analyses.append(hash_analysis)

    nsrl_socket.close()

    logging.debug(
        u'Closed connection to {0:s}:{1:d}'.format(self._host, self._port))

    return hash_analyses