    def _get_ssl_vhost_path(self, non_ssl_vh_fp):
        """ Get a file path for SSL vhost, uses user defined path as priority,
        but if the value is invalid or not defined, will fall back to non-ssl
        vhost filepath.

        :param str non_ssl_vh_fp: Filepath of non-SSL vhost

        :returns: Filepath for SSL vhost
        :rtype: str
        """

        if self.conf("vhost-root") and os.path.exists(self.conf("vhost-root")):
            # Defined by user on CLI

            fp = os.path.join(os.path.realpath(self.vhostroot),
                              os.path.basename(non_ssl_vh_fp))
        else:
            # Use non-ssl filepath
            fp = os.path.realpath(non_ssl_vh_fp)

        if fp.endswith(".conf"):
            return fp[:-(len(".conf"))] + self.conf("le_vhost_ext")
        else:
            return fp + self.conf("le_vhost_ext")