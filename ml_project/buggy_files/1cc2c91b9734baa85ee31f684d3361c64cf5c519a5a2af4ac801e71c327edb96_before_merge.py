  def ParseOptions(self, options):
    """Parses tool specific options.

    Args:
      options: the command line arguments (instance of argparse.Namespace).
    """
    self._ParseInformationalOptions(options)
    self._ParseDataLocationOption(options)