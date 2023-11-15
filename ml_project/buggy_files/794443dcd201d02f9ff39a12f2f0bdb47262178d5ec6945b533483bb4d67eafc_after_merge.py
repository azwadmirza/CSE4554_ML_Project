    def decrypt_file(self, filename, output_file=None):

        # follow the symlink
        filename = self._real_path(filename)

        ciphertext = self.read_data(filename)

        try:
            plaintext = self.vault.decrypt(ciphertext, filename=filename)
        except AnsibleError as e:
            raise AnsibleError("%s for %s" % (to_native(e), to_native(filename)))
        self.write_data(plaintext, output_file or filename, shred=False)