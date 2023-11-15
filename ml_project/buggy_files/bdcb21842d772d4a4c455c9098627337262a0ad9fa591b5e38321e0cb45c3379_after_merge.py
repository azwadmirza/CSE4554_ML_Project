  def ParseOptions(self, options):
    """Parses the options.

    Args:
      options: the command line arguments (instance of argparse.Namespace).

    Raises:
      BadConfigOption: if the options are invalid.
    """
    # Check the list options first otherwise required options will raise.
    self._ParseLanguageOptions(options)
    self._ParseTimezoneOption(options)

    if (self.list_analysis_plugins or self.list_language_identifiers or
        self.list_output_modules or self.list_timezones):
      return

    super(PsortTool, self).ParseOptions(options)
    self._ParseDataLocationOption(options)

    self._ParseAnalysisPluginOptions(options)
    self._ParseFilterOptions(options)

    debug = getattr(options, u'debug', False)
    if debug:
      logging_level = logging.DEBUG
    else:
      logging_level = logging.INFO

    logging.basicConfig(
        level=logging_level, format=u'[%(levelname)s] %(message)s')

    self._output_format = getattr(options, u'output_format', None)
    if not self._output_format:
      raise errors.BadConfigOption(u'Missing output format.')

    if not self._front_end.HasOutputClass(self._output_format):
      raise errors.BadConfigOption(
          u'Unsupported output format: {0:s}.'.format(self._output_format))

    self._deduplicate_events = getattr(options, u'dedup', True)

    self._output_filename = getattr(options, u'write', None)

    self._preferred_language = getattr(options, u'preferred_language', u'en-US')

    if not self._data_location:
      logging.warning(u'Unable to automatically determine data location.')

    # TODO: refactor this.
    self._options = options