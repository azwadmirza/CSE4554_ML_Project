    def prepare(self):
        """Prepare the authenticator/installer.

        :raises .errors.NoInstallationError: If Apache configs cannot be found
        :raises .errors.MisconfigurationError: If Apache is misconfigured
        :raises .errors.NotSupportedError: If Apache version is not supported
        :raises .errors.PluginError: If there is any other error

        """
        # Perform the actual Augeas initialization to be able to react
        try:
            self.init_augeas()
        except ImportError:
            raise errors.NoInstallationError("Problem in Augeas installation")

        # Verify Apache is installed
        restart_cmd = constants.os_constant("restart_cmd")[0]
        if not util.exe_exists(restart_cmd):
            if not path_surgery(restart_cmd):
                raise errors.NoInstallationError(
                    'Cannot find Apache control command {0}'.format(restart_cmd))

        # Make sure configuration is valid
        self.config_test()

        # Set Version
        if self.version is None:
            self.version = self.get_version()
            logger.debug('Apache version is %s',
                         '.'.join(str(i) for i in self.version))
        if self.version < (2, 2):
            raise errors.NotSupportedError(
                "Apache Version %s not supported.", str(self.version))

        if not self._check_aug_version():
            raise errors.NotSupportedError(
                "Apache plugin support requires libaugeas0 and augeas-lenses "
                "version 1.2.0 or higher, please make sure you have you have "
                "those installed.")

        self.parser = parser.ApacheParser(
            self.aug, self.conf("server-root"), self.conf("vhost-root"),
            self.version)
        # Check for errors in parsing files with Augeas
        self.check_parsing_errors("httpd.aug")

        # Get all of the available vhosts
        self.vhosts = self.get_virtual_hosts()

        install_ssl_options_conf(self.mod_ssl_conf, self.updated_mod_ssl_conf_digest)

        # Prevent two Apache plugins from modifying a config at once
        try:
            util.lock_dir_until_exit(self.conf("server-root"))
        except (OSError, errors.LockError):
            logger.debug("Encountered error:", exc_info=True)
            raise errors.PluginError(
                "Unable to lock %s", self.conf("server-root"))