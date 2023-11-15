  def _ParseDataLocationOption(self, options):
    """Parses the data location option.

    Args:
      options: the command line arguments (instance of argparse.Namespace).
    """
    data_location = getattr(options, u'data_location', None)
    if not data_location:
      # Determine if we are running from the source directory.
      # This should get us the path to the "plaso/cli" directory.
      data_location = os.path.dirname(__file__)
      # In order to get to the main path of the egg file we need to traverse
      # two directories up.
      data_location = os.path.dirname(data_location)
      data_location = os.path.dirname(data_location)
      # There are two options: running from source or from an egg file.
      data_location_egg = os.path.join(data_location, u'share', u'plaso')
      data_location_source = os.path.join(data_location, u'data')

      if os.path.exists(data_location_egg):
        data_location = data_location_egg
      elif os.path.exists(data_location_source):
        data_location = data_location_source
      else:
        # Otherwise determine if there is shared plaso data location.
        data_location = os.path.join(sys.prefix, u'share', u'plaso')

        if not os.path.exists(data_location):
          data_location = None

    self._data_location = data_location