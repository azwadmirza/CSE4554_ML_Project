    def _get_ssl_vhost_path(self, non_ssl_vh_fp):
        # Get filepath of new ssl_vhost
        if non_ssl_vh_fp.endswith(".conf"):
            return non_ssl_vh_fp[:-(len(".conf"))] + self.conf("le_vhost_ext")
        else:
            return non_ssl_vh_fp + self.conf("le_vhost_ext")