    def _add_name_vhost_if_necessary(self, vhost):
        """Add NameVirtualHost Directives if necessary for new vhost.

        NameVirtualHosts was a directive in Apache < 2.4
        https://httpd.apache.org/docs/2.2/mod/core.html#namevirtualhost

        :param vhost: New virtual host that was recently created.
        :type vhost: :class:`~letsencrypt_apache.obj.VirtualHost`

        """
        need_to_save = False

        # See if the exact address appears in any other vhost
        # Remember 1.1.1.1:* == 1.1.1.1 -> hence any()
        for addr in vhost.addrs:
            # In Apache 2.2, when a NameVirtualHost directive is not
            # set, "*" and "_default_" will conflict when sharing a port
            if addr.get_addr() in ("*", "_default_"):
                addrs = [obj.Addr((a, addr.get_port(),))
                         for a in ("*", "_default_")]

            for test_vh in self.vhosts:
                if (vhost.filep != test_vh.filep and
                        any(test_addr in addrs for
                            test_addr in test_vh.addrs) and
                        not self.is_name_vhost(addr)):
                    self.add_name_vhost(addr)
                    logger.info("Enabling NameVirtualHosts on %s", addr)
                    need_to_save = True

        if need_to_save:
            self.save()