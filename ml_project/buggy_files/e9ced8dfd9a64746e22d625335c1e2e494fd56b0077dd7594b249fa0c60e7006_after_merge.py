    def _pkey_auth(self, pkey_file, password=None):
        self.session.userauth_publickey_fromfile(
            self.user,
            pkey_file,
            passphrase=password if password is not None else '')