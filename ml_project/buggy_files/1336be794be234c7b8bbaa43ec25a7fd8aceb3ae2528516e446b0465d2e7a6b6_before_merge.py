  def Analyze(self, hashes):
    """Looks up hashes in nsrlsvr.

    Args:
      hashes (list[str]): hash values to look up.

    Returns:
      list[HashAnalysis]: analysis results, or an empty list on error.
    """
    # Open a socket
    logging.debug(
        u'Opening connection to {0:s}:{1:d}'.format(self._host, self._port))
    try:
      nsrl_socket = socket.create_connection(
          (self._host, self._port), self._SOCKET_TIMEOUT)
    except socket.error as exception:
      logging.error((
          u'Error communicating with nsrlsvr {0:s}. nsrlsvr plugin is '
          u'aborting.').format(exception))
      self.SignalAbort()
      return []

    hash_analyses = []
    for digest in hashes:
      query = u'QUERY {0:s}\n'.format(digest)
      try:
        nsrl_socket.sendall(query)
        response = nsrl_socket.recv(self._RECEIVE_BUFFER_SIZE)
      except socket.error as exception:
        logging.error(
            (u'Error communicating with nsrlsvr {0:s}. nsrlsvr plugin is '
             u'aborting.').format(exception))
        self.SignalAbort()
        return hash_analyses

      _, _, nsrl_result = response.rpartition(u' ')

      if nsrl_result == u'1':
        hash_analysis = interface.HashAnalysis(digest, True)
        hash_analyses.append(hash_analysis)
      else:
        hash_analysis = interface.HashAnalysis(digest, False)
        hash_analyses.append(hash_analysis)
    nsrl_socket.close()

    return hash_analyses