  def SetProtocol(self, protocol):
    """Sets the protocol that will be used to query Viper.

    Args:
      protocol (str): protocol to use to query Viper. Either 'http' or 'https'.

    Raises:
      ValueError: If an invalid protocol is selected.
    """
    protocol = protocol.lower().strip()
    if protocol not in [u'http', u'https']:
      raise ValueError(u'Invalid protocol specified for Viper lookup')
    self._analyzer.SetProtocol(protocol)