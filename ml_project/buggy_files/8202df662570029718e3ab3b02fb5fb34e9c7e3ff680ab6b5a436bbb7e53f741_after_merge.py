    def enable_site(self, vhost):
        """Enables an available site, Apache reload required.

        .. note:: Does not make sure that the site correctly works or that all
                  modules are enabled appropriately.

        .. todo:: This function should number subdomains before the domain
                  vhost

        .. todo:: Make sure link is not broken...

        :param vhost: vhost to enable
        :type vhost: :class:`~certbot_apache.obj.VirtualHost`

        :raises .errors.NotSupportedError: If filesystem layout is not
            supported.

        """
        if vhost.enabled:
            return

        # Handle non-debian systems
        if not self.conf("handle-sites"):
            if not self.parser.parsed_in_original(vhost.filep):
                # Add direct include to root conf
                self.parser.add_include(self.parser.loc["default"], vhost.filep)
                vhost.enabled = True
            return

        enabled_path = ("%s/sites-enabled/%s" %
                        (self.parser.root, os.path.basename(vhost.filep)))
        self.reverter.register_file_creation(False, enabled_path)
        try:
            os.symlink(vhost.filep, enabled_path)
        except OSError as err:
            if os.path.islink(enabled_path) and os.path.realpath(
               enabled_path) == vhost.filep:
                # Already in shape
                vhost.enabled = True
                return
            else:
                logger.warning(
                    "Could not symlink %s to %s, got error: %s", enabled_path,
                    vhost.filep, err.strerror)
                errstring = ("Encountered error while trying to enable a " +
                             "newly created VirtualHost located at {0} by " +
                             "linking to it from {1}")
                raise errors.NotSupportedError(errstring.format(vhost.filep,
                                                                enabled_path))
        vhost.enabled = True
        logger.info("Enabling available site: %s", vhost.filep)
        self.save_notes += "Enabled site %s\n" % vhost.filep