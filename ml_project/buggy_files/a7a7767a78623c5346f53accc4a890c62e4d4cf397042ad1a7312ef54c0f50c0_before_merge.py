  def ParseOptions(cls, options, analysis_plugin):
    """Parses and validates options.

    Args:
      options: the parser option object (instance of argparse.Namespace).
      analysis_plugin: an analysis plugin (instance of OutputModule).

    Raises:
      BadConfigObject: when the output module object is of the wrong type.
      BadConfigOption: when a configuration parameter fails validation.
    """
    if not isinstance(analysis_plugin, tagging.TaggingPlugin):
      raise errors.BadConfigObject(
          u'Analysis plugin is not an instance of TaggingPlugin')

    tagging_file = getattr(options, u'tagging_file', None)
    if tagging_file is None:
      raise errors.BadConfigOption(u'Tagging file path not set.')

    analysis_plugin.SetAndLoadTagFile(tagging_file)