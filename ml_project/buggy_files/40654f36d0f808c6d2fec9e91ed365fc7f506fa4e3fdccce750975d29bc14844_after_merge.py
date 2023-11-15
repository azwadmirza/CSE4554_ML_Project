    def dump(self):
        return {
            'type': self.type,
            'hw_type': self.hw_type,
            'xpub': self.xpub,
            'derivation': self.get_derivation_prefix(),
            'root_fingerprint': self.get_root_fingerprint(),
            'label':self.label,
            'soft_device_id': self.soft_device_id,
        }