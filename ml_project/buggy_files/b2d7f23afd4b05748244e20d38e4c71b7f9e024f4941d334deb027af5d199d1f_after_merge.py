    def make_vhost_ssl(self, nonssl_vhost):  # pylint: disable=too-many-locals
        """Makes an ssl_vhost version of a nonssl_vhost.

        Duplicates vhost and adds default ssl options
        New vhost will reside as (nonssl_vhost.path) +
        ``certbot_apache.constants.os_constant("le_vhost_ext")``

        .. note:: This function saves the configuration

        :param nonssl_vhost: Valid VH that doesn't have SSLEngine on
        :type nonssl_vhost: :class:`~certbot_apache.obj.VirtualHost`

        :returns: SSL vhost
        :rtype: :class:`~certbot_apache.obj.VirtualHost`

        :raises .errors.PluginError: If more than one virtual host is in
            the file or if plugin is unable to write/read vhost files.

        """
        avail_fp = nonssl_vhost.filep
        ssl_fp = self._get_ssl_vhost_path(avail_fp)

        orig_matches = self.aug.match("/files%s//* [label()=~regexp('%s')]" %
                                      (self._escape(ssl_fp),
                                       parser.case_i("VirtualHost")))

        self._copy_create_ssl_vhost_skeleton(nonssl_vhost, ssl_fp)

        # Reload augeas to take into account the new vhost
        self.aug.load()
        # Get Vhost augeas path for new vhost
        new_matches = self.aug.match("/files%s//* [label()=~regexp('%s')]" %
                                     (self._escape(ssl_fp),
                                      parser.case_i("VirtualHost")))

        vh_p = self._get_new_vh_path(orig_matches, new_matches)

        if not vh_p:
            # The vhost was not found on the currently parsed paths
            # Make Augeas aware of the new vhost
            self.parser.parse_file(ssl_fp)
            # Try to search again
            new_matches = self.aug.match(
                "/files%s//* [label()=~regexp('%s')]" %
                (self._escape(ssl_fp),
                 parser.case_i("VirtualHost")))
            vh_p = self._get_new_vh_path(orig_matches, new_matches)
            if not vh_p:
                raise errors.PluginError(
                    "Could not reverse map the HTTPS VirtualHost to the original")


        # Update Addresses
        self._update_ssl_vhosts_addrs(vh_p)

        # Log actions and create save notes
        logger.info("Created an SSL vhost at %s", ssl_fp)
        self.save_notes += "Created ssl vhost at %s\n" % ssl_fp
        self.save()

        # We know the length is one because of the assertion above
        # Create the Vhost object
        ssl_vhost = self._create_vhost(vh_p)
        ssl_vhost.ancestor = nonssl_vhost

        self.vhosts.append(ssl_vhost)

        # NOTE: Searches through Augeas seem to ruin changes to directives
        #       The configuration must also be saved before being searched
        #       for the new directives; For these reasons... this is tacked
        #       on after fully creating the new vhost

        # Now check if addresses need to be added as NameBasedVhost addrs
        # This is for compliance with versions of Apache < 2.4
        self._add_name_vhost_if_necessary(ssl_vhost)

        return ssl_vhost