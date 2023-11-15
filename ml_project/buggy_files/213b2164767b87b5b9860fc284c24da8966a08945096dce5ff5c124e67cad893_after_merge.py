    def sys_info(self):
        """Return a list of (key, value) pairs showing internal information."""

        import coverage as covmod

        self._init()
        self._post_init()

        def plugin_info(plugins):
            """Make an entry for the sys_info from a list of plug-ins."""
            entries = []
            for plugin in plugins:
                entry = plugin._coverage_plugin_name
                if not plugin._coverage_enabled:
                    entry += " (disabled)"
                entries.append(entry)
            return entries

        info = [
            ('version', covmod.__version__),
            ('coverage', covmod.__file__),
            ('tracer', self._collector.tracer_name() if self._collector else "-none-"),
            ('CTracer', 'available' if CTracer else "unavailable"),
            ('plugins.file_tracers', plugin_info(self._plugins.file_tracers)),
            ('plugins.configurers', plugin_info(self._plugins.configurers)),
            ('plugins.context_switchers', plugin_info(self._plugins.context_switchers)),
            ('configs_attempted', self.config.attempted_config_files),
            ('configs_read', self.config.config_files_read),
            ('config_file', self.config.config_file),
            ('config_contents',
                repr(self.config._config_contents)
                if self.config._config_contents
                else '-none-'
            ),
            ('data_file', self._data.data_filename() if self._data is not None else "-none-"),
            ('python', sys.version.replace('\n', '')),
            ('platform', platform.platform()),
            ('implementation', platform.python_implementation()),
            ('executable', sys.executable),
            ('def_encoding', sys.getdefaultencoding()),
            ('fs_encoding', sys.getfilesystemencoding()),
            ('pid', os.getpid()),
            ('cwd', os.getcwd()),
            ('path', sys.path),
            ('environment', sorted(
                ("%s = %s" % (k, v))
                for k, v in iitems(os.environ)
                if any(slug in k for slug in ("COV", "PY"))
            )),
            ('command_line', " ".join(getattr(sys, 'argv', ['-none-']))),
            ]

        if self._inorout:
            info.extend(self._inorout.sys_info())

        info.extend(CoverageData.sys_info())

        return info