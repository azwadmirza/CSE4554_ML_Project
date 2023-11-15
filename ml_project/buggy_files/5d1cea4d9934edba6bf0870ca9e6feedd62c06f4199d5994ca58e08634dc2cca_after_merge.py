  def RunModeRegistryPlugin(self):
    """Run against a set of Registry plugins."""
    # TODO: Add support for splitting the output to separate files based on
    # each plugin name.
    registry_helpers = self._front_end.GetRegistryHelpers(
        plugin_names=self.plugin_names)

    plugins = []
    for plugin_name in self.plugin_names:
      plugins.extend(self._front_end.GetRegistryPlugins(plugin_name))
    plugin_list = [plugin.NAME for plugin in plugins]

    # In order to get all the Registry keys we need to expand
    # them, but to do so we need to open up one hive so that we
    # create the reg_cache object, which is necessary to fully
    # expand all keys.
    if not registry_helpers:
      return

    registry_helper = registry_helpers[0]
    key_paths = []
    try:
      registry_helper.Open()
      parser_mediator = self._front_end.CreateParserMediator()

      plugins = self._front_end.registry_plugin_list

      # Get all the appropriate keys from these plugins.
      key_paths = plugins.GetExpandedKeyPaths(
          parser_mediator, reg_cache=registry_helper.reg_cache,
          plugin_names=plugin_list)
    finally:
      registry_helper.Close()

    for registry_helper in registry_helpers:
      parsed_data = self._front_end.ParseRegistryFile(
          registry_helper, key_paths=key_paths, use_plugins=plugin_list)
      self._PrintParsedRegistryFile(parsed_data, registry_helper)