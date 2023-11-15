  def ParseOptions(self, options):
    """Parses the options and initializes the front-end.

    Args:
      options: the command line arguments (instance of argparse.Namespace).

    Raises:
      BadConfigOption: if the options are invalid.
    """
    if not options:
      raise errors.BadConfigOption(u'Missing options.')

    self._storage_file_path = getattr(options, 'storage_file', None)
    if not self._storage_file_path:
      raise errors.BadConfigOption(u'Missing storage file.')

    if not os.path.isfile(self._storage_file_path):
      raise errors.BadConfigOption(
          u'No such storage file {0:s}.'.format(self._storage_file_path))