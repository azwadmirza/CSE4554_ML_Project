    def _decrypt(self, cipher):
        """Decrypts a cipher string using self.key as the key and the first 16 byte of the cipher as the IV"""
        if not cipher:
            return ""
        crypto = AES.new(self.key, AES.MODE_CBC, cipher[:16])
        plain = crypto.decrypt(cipher[16:])
        if plain[-1] != " ": # Journals are always padded
            return None
        else:
            return plain