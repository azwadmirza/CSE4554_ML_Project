    def generate(self, module):
        """Generate a keypair."""

        if not self.check(module, perms_required=False) or self.force:
            self.privatekey = crypto.PKey()

            try:
                self.privatekey.generate_key(self.type, self.size)
            except (TypeError, ValueError) as exc:
                raise PrivateKeyError(exc)

            try:
                privatekey_file = os.open(self.path,
                                          os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
                                          self.mode)

                if self.cipher and self.passphrase:
                    os.write(privatekey_file, crypto.dump_privatekey(crypto.FILETYPE_PEM, self.privatekey,
                                                                     self.cipher, to_bytes(self.passphrase)))
                else:
                    os.write(privatekey_file, crypto.dump_privatekey(crypto.FILETYPE_PEM, self.privatekey))
                os.close(privatekey_file)
                self.changed = True
            except IOError as exc:
                self.remove()
                raise PrivateKeyError(exc)

        self.fingerprint = crypto_utils.get_fingerprint(self.path, self.passphrase)
        file_args = module.load_file_common_arguments(module.params)
        if module.set_fs_attributes_if_different(file_args, False):
            self.changed = True