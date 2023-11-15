    def export_pubkey(self, name):
        fingerprint = self.getkey(name)
        return self.gpg.export_keys(fingerprint)