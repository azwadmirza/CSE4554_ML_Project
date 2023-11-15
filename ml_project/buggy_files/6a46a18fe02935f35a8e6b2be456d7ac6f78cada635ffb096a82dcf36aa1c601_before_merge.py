    def __init__(self, name_map, path, defaults=None, load=True, version=None,
                 backup=False, raw_mode=False, remove_obsolete=False):
        """Multi user config class based on UserConfig class."""
        self._name_map = self._check_name_map(name_map)
        self._path = path
        self._defaults = defaults
        self._load = load
        self._version = version
        self._backup = backup
        self._raw_mode = 1 if raw_mode else 0
        self._remove_obsolete = remove_obsolete

        self._configs_map = {}
        self._config_defaults_map = self._get_defaults_for_name_map(defaults,
                                                                    name_map)
        self._config_kwargs = {
            'path': path,
            'defaults': defaults,
            'load': load,
            'version': version,
            'backup': backup,
            'raw_mode': raw_mode,
            'remove_obsolete': False,  # This will be handled later on if True
        }

        for name in name_map:
            defaults = self._config_defaults_map.get(name)
            mod_kwargs = {
                'name': name,
                'defaults': defaults,
            }
            new_kwargs = self._config_kwargs.copy()
            new_kwargs.update(mod_kwargs)
            config_class = self.get_config_class()
            self._configs_map[name] = config_class(**new_kwargs)

        # Remove deprecated options if major version has changed
        default_config = self._configs_map.get(self.DEFAULT_FILE_NAME)
        major_ver = default_config._get_major_version(version)
        major_old_ver = default_config._get_major_version(
            default_config._old_version)

        # Now we can apply remove_obsolete
        if remove_obsolete or major_ver != major_old_ver:
            for _, config in self._configs_map.items():
                config._remove_deprecated_options(config._old_version)