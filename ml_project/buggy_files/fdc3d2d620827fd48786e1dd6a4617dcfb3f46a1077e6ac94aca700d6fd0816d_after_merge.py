  def SetHost(self, host):
    """Sets the address or hostname of the server running Viper server.

    Args:
      host (str): IP address or hostname to query.
    """
    self._analyzer.SetHost(host)