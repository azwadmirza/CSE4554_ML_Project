  def SetProtocol(self, protocol):
    """Sets the protocol that will be used to query Viper.

    Args:
      protocol: The protocol to use to query Viper. Either 'http' or 'https'.

    Raises:
      ValueError: If an invalid protocol is specified.
    """
    protocol = protocol.lower().strip()
    if protocol not in self._SUPPORTED_PROTOCOLS:
      raise ValueError(u'Invalid protocol specified for Viper lookup')
    self._protocol = protocol