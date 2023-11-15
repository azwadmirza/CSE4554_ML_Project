  def ParseOptions(self, options):
    """Parses the options.

    Args:
      options: the command line arguments (instance of argparse.Namespace).

    Raises:
      BadConfigOption: if the options are invalid.
    """
    if getattr(options, u'show_info', False):
      self.run_mode = self.RUN_MODE_LIST_PLUGINS
      return

    registry_file = getattr(options, u'registry_file', None)
    image = getattr(options, u'image', None)
    source_path = None
    if image:
      # TODO: refactor, there should be no need for separate code paths.
      super(PregTool, self).ParseOptions(options)
      source_path = image
      self._front_end.SetSingleFile(False)
    else:
      self._ParseInformationalOptions(options)
      source_path = registry_file
      self._front_end.SetSingleFile(True)

    if source_path is None:
      raise errors.BadConfigOption(u'No source path set.')

    self._front_end.SetSourcePath(source_path)
    self._source_path = os.path.abspath(source_path)

    if not image and not registry_file:
      raise errors.BadConfigOption(u'Not enough parameters to proceed.')

    if registry_file:
      if not image and not os.path.isfile(registry_file):
        raise errors.BadConfigOption(
            u'Registry file: {0:s} does not exist.'.format(registry_file))

    self._key_path = getattr(options, u'key', None)
    self._parse_restore_points = getattr(options, u'restore_points', False)

    self._quiet = getattr(options, u'quiet', False)

    self._verbose_output = getattr(options, u'verbose', False)

    if image:
      file_to_check = image
    else:
      file_to_check = registry_file

    is_file, reason = self._PathExists(file_to_check)
    if not is_file:
      raise errors.BadConfigOption(
          u'Unable to read the input file with error: {0:s}'.format(reason))

    self.plugin_names = getattr(options, u'plugin_names', [])

    self._front_end.SetKnowledgeBase(self._knowledge_base_object)

    if getattr(options, u'console', False):
      self.run_mode = self.RUN_MODE_CONSOLE
    elif getattr(options, u'key', u'') and registry_file:
      self.run_mode = self.RUN_MODE_REG_KEY
    elif self.plugin_names:
      self.run_mode = self.RUN_MODE_REG_PLUGIN
    elif registry_file:
      self.run_mode = self.RUN_MODE_REG_FILE
    else:
      raise errors.BadConfigOption(
          u'Incorrect usage. You\'ll need to define the path of either '
          u'a storage media image or a Windows Registry file.')

    self.registry_file = registry_file

    scan_context = self.ScanSource()
    self.source_type = scan_context.source_type
    self._front_end.SetSourcePathSpecs(self._source_path_specs)