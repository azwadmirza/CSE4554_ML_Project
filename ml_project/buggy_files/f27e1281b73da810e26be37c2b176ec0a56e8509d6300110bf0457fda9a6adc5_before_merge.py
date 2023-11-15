    def __populate_analyzers(self):
        """ Set analyzer binaries for each registered analyzers. """
        analyzer_env = None
        analyzer_from_path = env.is_analyzer_from_path()
        if not analyzer_from_path:
            analyzer_env = env.extend(self.path_env_extra,
                                      self.ld_lib_path_extra)

        compiler_binaries = self.pckg_layout.get('analyzers')
        for name, value in compiler_binaries.items():

            if analyzer_from_path:
                value = os.path.basename(value)

            if os.path.dirname(value):
                # Check if it is a package relative path.
                self.__analyzers[name] = os.path.join(self._package_root,
                                                      value)
            else:
                env_path = analyzer_env['PATH'] if analyzer_env else None
                compiler_binary = find_executable(value, env_path)
                if not compiler_binary:
                    LOG.warning("'%s' binary can not be found in your PATH!",
                                value)
                    continue

                self.__analyzers[name] = os.path.realpath(compiler_binary)