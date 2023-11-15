    def from_file(self, filename, our_file):
        """Read configuration from a .rc file.

        `filename` is a file name to read.

        `our_file` is True if this config file is specifically for coverage,
        False if we are examining another config file (tox.ini, setup.cfg)
        for possible settings.

        Returns True or False, whether the file could be read, and it had some
        coverage.py settings in it.

        """
        _, ext = os.path.splitext(filename)
        if ext == '.toml':
            cp = TomlConfigParser(our_file)
        else:
            cp = HandyConfigParser(our_file)

        self.attempted_config_files.append(filename)

        try:
            files_read = cp.read(filename)
        except (configparser.Error, TomlDecodeError) as err:
            raise CoverageException("Couldn't read config file %s: %s" % (filename, err))
        if not files_read:
            return False

        self.config_files_read.extend(files_read)

        any_set = False
        try:
            for option_spec in self.CONFIG_FILE_OPTIONS:
                was_set = self._set_attr_from_config_option(cp, *option_spec)
                if was_set:
                    any_set = True
        except ValueError as err:
            raise CoverageException("Couldn't read config file %s: %s" % (filename, err))

        # Check that there are no unrecognized options.
        all_options = collections.defaultdict(set)
        for option_spec in self.CONFIG_FILE_OPTIONS:
            section, option = option_spec[1].split(":")
            all_options[section].add(option)

        for section, options in iitems(all_options):
            real_section = cp.has_section(section)
            if real_section:
                for unknown in set(cp.options(section)) - options:
                    raise CoverageException(
                        "Unrecognized option '[%s] %s=' in config file %s" % (
                            real_section, unknown, filename
                        )
                    )

        # [paths] is special
        if cp.has_section('paths'):
            for option in cp.options('paths'):
                self.paths[option] = cp.getlist('paths', option)
                any_set = True

        # plugins can have options
        for plugin in self.plugins:
            if cp.has_section(plugin):
                self.plugin_options[plugin] = cp.get_section(plugin)
                any_set = True

        # Was this file used as a config file? If it's specifically our file,
        # then it was used.  If we're piggybacking on someone else's file,
        # then it was only used if we found some settings in it.
        if our_file:
            used = True
        else:
            used = any_set

        if used:
            self.config_file = filename
            with open(filename) as f:
                self._config_contents = f.read()

        return used