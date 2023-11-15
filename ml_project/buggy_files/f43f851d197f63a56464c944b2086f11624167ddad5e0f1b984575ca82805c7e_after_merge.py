    def encrypt_file(self, filename, output_file=None):

        check_prereqs()

        # A file to be encrypted into a vaultfile could be any encoding
        # so treat the contents as a byte string.
        b_plaintext = self.read_data(filename)
        b_ciphertext = self.vault.encrypt(b_plaintext)
        self.write_data(b_ciphertext, output_file or filename)