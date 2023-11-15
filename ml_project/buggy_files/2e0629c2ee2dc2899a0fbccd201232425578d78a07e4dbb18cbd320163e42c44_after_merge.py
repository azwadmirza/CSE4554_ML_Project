    def register_plugin(self, plugin_class):
        """Register plugin configuration."""
        conf_section = plugin_class.CONF_SECTION
        if plugin_class.CONF_FILE and conf_section:
            path = self.get_plugin_config_path(conf_section)
            version = plugin_class.CONF_VERSION
            version = version if version else '0.0.0'
            name_map = plugin_class._CONF_NAME_MAP
            name_map = name_map if name_map else {'spyder': []}
            defaults = plugin_class.CONF_DEFAULTS

            if conf_section in self._plugin_configs:
                raise RuntimeError('A plugin with section "{}" already '
                                   'exists!'.format(conf_section))

            plugin_config = MultiUserConfig(
                name_map,
                path=path,
                defaults=defaults,
                load=True,
                version=version,
                backup=True,
                raw_mode=True,
                remove_obsolete=False,
                external_plugin=True
            )

            # Recreate external plugin configs to deal with part two
            # (the shortcut conflicts) of spyder-ide/spyder#11132
            spyder_config = self._user_config._configs_map['spyder']
            if check_version(spyder_config._old_version, '54.0.0', '<'):
                # Remove all previous .ini files
                try:
                    plugin_config.cleanup()
                except EnvironmentError:
                    pass

                # Recreate config
                plugin_config = MultiUserConfig(
                    name_map,
                    path=path,
                    defaults=defaults,
                    load=True,
                    version=version,
                    backup=True,
                    raw_mode=True,
                    remove_obsolete=False,
                    external_plugin=True
                )

            self._plugin_configs[conf_section] = (plugin_class, plugin_config)