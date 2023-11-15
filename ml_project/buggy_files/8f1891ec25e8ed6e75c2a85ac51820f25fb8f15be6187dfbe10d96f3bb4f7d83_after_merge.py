    def _create_vhost(self, path):
        """Used by get_virtual_hosts to create vhost objects

        :param str path: Augeas path to virtual host

        :returns: newly created vhost
        :rtype: :class:`~certbot_apache.obj.VirtualHost`

        """
        addrs = set()
        try:
            args = self.aug.match(path + "/arg")
        except RuntimeError:
            logger.warning("Encountered a problem while parsing file: %s, skipping", path)
            return None
        for arg in args:
            addrs.add(obj.Addr.fromstring(self.parser.get_arg(arg)))
        is_ssl = False

        if self.parser.find_dir("SSLEngine", "on", start=path, exclude=False):
            is_ssl = True

        # "SSLEngine on" might be set outside of <VirtualHost>
        # Treat vhosts with port 443 as ssl vhosts
        for addr in addrs:
            if addr.get_port() == "443":
                is_ssl = True

        filename = get_file_path(self.aug.get("/augeas/files%s/path" % get_file_path(path)))
        if filename is None:
            return None

        macro = False
        if "/macro/" in path.lower():
            macro = True

        vhost_enabled = self.parser.parsed_in_original(filename)

        vhost = obj.VirtualHost(filename, path, addrs, is_ssl,
                                vhost_enabled, modmacro=macro)
        self._add_servernames(vhost)
        return vhost