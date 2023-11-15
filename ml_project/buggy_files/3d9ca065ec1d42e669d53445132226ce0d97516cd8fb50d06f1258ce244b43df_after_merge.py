  def ParseOptions(self, options):
    """Parses the options and initializes the front-end.

    Args:
      options: the command line arguments (instance of argparse.Namespace).
      source_option: optional name of the source option. The default is source.

    Raises:
      BadConfigOption: if the options are invalid.
    """
    # TODO: Refactor to avoid this hack.
    # This means we parse the data location twice, (the other time is in
    # CLITool.ParseOptions) but it's required to get the signatures to be
    # listed.
    self._ParseDataLocationOption(options)
    # Check the list options first otherwise required options will raise.
    signature_identifiers = getattr(options, u'signature_identifiers', None)
    if signature_identifiers == u'list':
      self.list_signature_identifiers = True

    if self.list_signature_identifiers:
      return

    super(ImageExportTool, self).ParseOptions(options)

    format_str = u'%(asctime)s [%(levelname)s] %(message)s'

    if self._debug_mode:
      logging.basicConfig(level=logging.DEBUG, format=format_str)
    else:
      logging.basicConfig(level=logging.INFO, format=format_str)

    self._destination_path = getattr(options, u'path', u'export')

    filter_file = getattr(options, u'filter', None)
    if filter_file and not os.path.isfile(filter_file):
      raise errors.BadConfigOption(
          u'Unable to proceed, filter file: {0:s} does not exist.'.format(
              filter_file))

    self._filter_file = filter_file

    if (getattr(options, u'no_vss', False) or
        getattr(options, u'include_duplicates', False)):
      self._remove_duplicates = False

    date_filters = getattr(options, u'date_filters', None)
    try:
      self._front_end.ParseDateFilters(date_filters)
    except ValueError as exception:
      raise errors.BadConfigOption(exception)

    extensions_string = getattr(options, u'extensions_string', None)
    self._front_end.ParseExtensionsString(extensions_string)

    names_string = getattr(options, u'names_string', None)
    self._front_end.ParseNamesString(names_string)

    if not self._data_location:
      logging.warning(u'Unable to automatically determine data location.')

    signature_identifiers = getattr(options, u'signature_identifiers', None)
    try:
      self._front_end.ParseSignatureIdentifiers(
          self._data_location, signature_identifiers)
    except (IOError, ValueError) as exception:
      raise errors.BadConfigOption(exception)

    self.has_filters = self._front_end.HasFilters()