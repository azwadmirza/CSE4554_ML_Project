    def encrypt_file(self, filename, output_file=None):

        check_prereqs()

        # A file to be encrypted into a vaultfile could be any encoding
        # so treat the contents as a byte string.
        plaintext = self.read_data(filename)
        ciphertext = self.vault.encrypt(plaintext)
        self.write_data(ciphertext, output_file or filename)