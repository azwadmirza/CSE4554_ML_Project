  def _ExtractExtensionInstallationEvents(self, settings_dict):
    """Extract extension installation events.

    Args:
      settings_dict: A dictionary of settings data from Preferences file.

    Yields:
      A tuple of: install_time, extension_id, extension_name, path.
    """
    for extension_id, extension in settings_dict.iteritems():
      try:
        install_time = int(extension.get(u'install_time', u'0'), 10)
      except ValueError as exception:
        logging.warning(
            u'Extension ID {0:s} is missing timestamp: {1:s}'.format(
                extension_id, exception))
        continue
      manifest = extension.get(u'manifest')
      if manifest:
        extension_name = manifest.get(u'name')
      else:
        extension_name = None
      path = extension.get(u'path')
      yield install_time, extension_id, extension_name, path