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

        self.mode = module.params['mode']
        if not self.mode:
            self.mode = int('0600', 8)

        self.type = crypto.TYPE_RSA
        if module.params['type'] == 'DSA':
            self.type = crypto.TYPE_DSA