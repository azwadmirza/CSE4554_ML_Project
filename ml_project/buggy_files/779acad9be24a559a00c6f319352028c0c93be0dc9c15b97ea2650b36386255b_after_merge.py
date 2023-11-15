    def __init__(self, name, path, defaults=None, load=True, version=None,
                 backup=False, raw_mode=False, remove_obsolete=False,
                 external_plugin=False):
        """UserConfig class, based on ConfigParser."""
        super(UserConfig, self).__init__(name=name, path=path)

        self._load = load
        self._version = self._check_version(version)
        self._backup = backup
        self._raw = 1 if raw_mode else 0
        self._remove_obsolete = remove_obsolete
        self._external_plugin = external_plugin

        self._module_source_path = get_module_source_path('spyder')
        self._defaults_folder = 'defaults'
        self._backup_folder = 'backups'
        self._backup_suffix = '.bak'
        self._defaults_name_prefix = 'defaults'

        # This attribute is overriding a method from cp.ConfigParser
        self.defaults = self._check_defaults(defaults)

        if backup:
            self._make_backup()

        if load:
            # If config file already exists, it overrides Default options
            previous_fpath = self.get_previous_config_fpath()
            self._load_from_ini(previous_fpath)
            old_version = self.get_version(version)
            self._old_version = old_version

            # Save new defaults
            self._save_new_defaults(self.defaults)

            # Updating defaults only if major/minor version is different
            if (self._get_minor_version(version)
                    != self._get_minor_version(old_version)):

                if backup:
                    self._make_backup(version=old_version)

                self.apply_configuration_patches(old_version=old_version)

                # Remove deprecated options if major version has changed
                if remove_obsolete:
                    self._remove_deprecated_options(old_version)

                # Set new version number
                self.set_version(version, save=False)

            if defaults is None:
                # If no defaults are defined set .ini file settings as default
                self.set_as_defaults()