    def dump(self, check_mode=False):

        result = {
            'changed': self.changed,
            'filename': self.path,
            'privatekey': self.privatekey_path,
            'csr': self.csr_path
        }

        if check_mode:
            now = datetime.datetime.utcnow()
            ten = now.replace(now.year + 10)
            result.update({
                'notBefore': self.notBefore if self.notBefore else now.strftime("%Y%m%d%H%M%SZ"),
                'notAfter': self.notAfter if self.notAfter else ten.strftime("%Y%m%d%H%M%SZ"),
                'serial_number': self.serial_number,
            })
        else:
            result.update({
                'notBefore': self.cert.get_notBefore(),
                'notAfter': self.cert.get_notAfter(),
                'serial_number': self.cert.get_serial_number(),
            })

        return result