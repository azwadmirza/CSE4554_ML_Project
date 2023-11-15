    def parse_build_isolation(self, config, reader):
        config.isolated_build = reader.getbool("isolated_build", False)
        config.isolated_build_env = reader.getstring("isolated_build_env", ".package")
        if config.isolated_build is True:
            name = config.isolated_build_env
            section_name = "testenv:{}".format(name)
            if section_name not in self._cfg.sections:
                self._cfg.sections[section_name] = {}
            self._cfg.sections[section_name]["deps"] = ""
            self._cfg.sections[section_name]["sitepackages"] = "False"
            self._cfg.sections[section_name]["description"] = "isolated packaging environment"
            config.envconfigs[name] = self.make_envconfig(
                name, "{}{}".format(testenvprefix, name), reader._subs, config
            )