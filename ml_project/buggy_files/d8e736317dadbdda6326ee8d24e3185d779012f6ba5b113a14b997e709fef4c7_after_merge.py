    def __init__(self, module):
        super(PrivateKey, self).__init__(
            module.params['path'],
            module.params['state'],
            module.params['force'],
            module.check_mode
        )
        self.size = module.params['size']
        self.passphrase = module.params['passphrase']
        self.cipher = module.params['cipher']
        self.privatekey = None
        self.fingerprint = {}

        self.mode = module.params.get('mode', None)
        if self.mode is None:
            self.mode = 0o600

        self.type = crypto.TYPE_RSA
        if module.params['type'] == 'DSA':
            self.type = crypto.TYPE_DSA