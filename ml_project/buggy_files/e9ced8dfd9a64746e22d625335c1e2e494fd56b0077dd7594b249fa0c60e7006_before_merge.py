    def _pkey_auth(self, password=None):
        self.session.userauth_publickey_fromfile(
            self.user,
            self.pkey,
            passphrase=password if password is not None else '')