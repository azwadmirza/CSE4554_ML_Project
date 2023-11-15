    def _mod_config(self):
        """Modifies Apache config files to include challenge vhosts.

        Result: Apache config includes virtual servers for issued challs

        :returns: All TLS-SNI-01 addresses used
        :rtype: set

        """
        addrs = set()
        config_text = "<IfModule mod_ssl.c>\n"

        for achall in self.achalls:
            achall_addrs = self._get_addrs(achall)
            addrs.update(achall_addrs)

            config_text += self._get_config_text(achall, achall_addrs)

        config_text += "</IfModule>\n"

        self.configurator.parser.add_include(
            self.configurator.parser.loc["default"], self.challenge_conf)
        self.configurator.reverter.register_file_creation(
            True, self.challenge_conf)

        logger.debug("writing a config file with text:\n %s", config_text)
        with open(self.challenge_conf, "w") as new_conf:
            new_conf.write(config_text)

        return addrs