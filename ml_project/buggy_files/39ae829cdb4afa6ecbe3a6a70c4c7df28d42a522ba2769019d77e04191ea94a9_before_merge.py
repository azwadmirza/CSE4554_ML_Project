    def deploy_cert(self, domain, cert_path, key_path,
                    chain_path=None, fullchain_path=None):
        """Deploys certificate to specified virtual host.

        Currently tries to find the last directives to deploy the cert in
        the VHost associated with the given domain. If it can't find the
        directives, it searches the "included" confs. The function verifies
        that it has located the three directives and finally modifies them
        to point to the correct destination. After the certificate is
        installed, the VirtualHost is enabled if it isn't already.

        .. todo:: Might be nice to remove chain directive if none exists
                  This shouldn't happen within certbot though

        :raises errors.PluginError: When unable to deploy certificate due to
            a lack of directives

        """
        vhost = self.choose_vhost(domain)
        self._clean_vhost(vhost)

        # This is done first so that ssl module is enabled and cert_path,
        # cert_key... can all be parsed appropriately
        self.prepare_server_https("443")

        path = {"cert_path": self.parser.find_dir("SSLCertificateFile",
                                                  None, vhost.path),
                "cert_key": self.parser.find_dir("SSLCertificateKeyFile",
                                                 None, vhost.path)}

        # Only include if a certificate chain is specified
        if chain_path is not None:
            path["chain_path"] = self.parser.find_dir(
                "SSLCertificateChainFile", None, vhost.path)

        if not path["cert_path"] or not path["cert_key"]:
            # Throw some can't find all of the directives error"
            logger.warning(
                "Cannot find a cert or key directive in %s. "
                "VirtualHost was not modified", vhost.path)
            # Presumably break here so that the virtualhost is not modified
            raise errors.PluginError(
                "Unable to find cert and/or key directives")

        logger.info("Deploying Certificate for %s to VirtualHost %s", domain, vhost.filep)

        if self.version < (2, 4, 8) or (chain_path and not fullchain_path):
            # install SSLCertificateFile, SSLCertificateKeyFile,
            # and SSLCertificateChainFile directives
            set_cert_path = cert_path
            self.aug.set(path["cert_path"][-1], cert_path)
            self.aug.set(path["cert_key"][-1], key_path)
            if chain_path is not None:
                self.parser.add_dir(vhost.path,
                                    "SSLCertificateChainFile", chain_path)
            else:
                raise errors.PluginError("--chain-path is required for your "
                                         "version of Apache")
        else:
            if not fullchain_path:
                raise errors.PluginError("Please provide the --fullchain-path\
 option pointing to your full chain file")
            set_cert_path = fullchain_path
            self.aug.set(path["cert_path"][-1], fullchain_path)
            self.aug.set(path["cert_key"][-1], key_path)

        # Save notes about the transaction that took place
        self.save_notes += ("Changed vhost at %s with addresses of %s\n"
                            "\tSSLCertificateFile %s\n"
                            "\tSSLCertificateKeyFile %s\n" %
                            (vhost.filep,
                             ", ".join(str(addr) for addr in vhost.addrs),
                             set_cert_path, key_path))
        if chain_path is not None:
            self.save_notes += "\tSSLCertificateChainFile %s\n" % chain_path

        # Make sure vhost is enabled if distro with enabled / available
        if self.conf("handle-sites"):
            if not vhost.enabled:
                self.enable_site(vhost)