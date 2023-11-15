    def _pkey_auth(self, password=None):
        pkey = import_privkey_file(self.pkey, passphrase=password if password is not None else '')
        if self.cert_file is not None:
            logger.debug("Certificate file set - trying certificate authentication")
            self._import_cert_file(pkey)
        self.session.userauth_publickey(pkey)