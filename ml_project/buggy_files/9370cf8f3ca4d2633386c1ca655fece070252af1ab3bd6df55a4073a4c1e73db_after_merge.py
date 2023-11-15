    def export_pubkey(self, name):
        fingerprint = self.getkey(name)
        if fingerprint:
            return self.gpg.export_keys(fingerprint)
        else:
            return None