    def dump(self):

        result = {
            'changed': self.changed,
            'filename': self.path,
            'privatekey': self.privatekey_path,
            'csr': self.csr_path,
            'notBefore': self.cert.get_notBefore(),
            'notAfter': self.cert.get_notAfter(),
            'serial_number': self.cert.get_serial_number(),
        }

        return result