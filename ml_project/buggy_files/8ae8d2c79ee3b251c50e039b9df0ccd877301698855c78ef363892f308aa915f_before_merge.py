  def ParseFileObject(self, parser_mediator, file_object, **kwargs):
    """Parses a Windows Registry file-like object.

    Args:
      parser_mediator: a parser mediator object (instance of ParserMediator).
      file_object: a file-like object.
    """
    win_registry_reader = FileObjectWinRegistryFileReader()
    registry_file = win_registry_reader.Open(file_object)

    win_registry = dfwinreg_registry.WinRegistry()
    key_path_prefix = win_registry.GetRegistryFileMapping(registry_file)
    registry_file.SetKeyPathPrefix(key_path_prefix)
    root_key = registry_file.GetRootKey()
    if not root_key:
      return

    try:
      for registry_key in root_key.RecurseKeys():
        # TODO: use a filter tree to optimize lookups.
        found_matching_plugin = False
        for plugin_object in self._plugins:
          if parser_mediator.abort:
            break

          if self._CanProcessKeyWithPlugin(registry_key, plugin_object):
            found_matching_plugin = True
            plugin_object.UpdateChainAndProcess(parser_mediator, registry_key)

        if not found_matching_plugin:
          self._default_plugin.UpdateChainAndProcess(
              parser_mediator, registry_key)

    except IOError as exception:
      parser_mediator.ProduceParseError(u'{0:s}'.format(exception))