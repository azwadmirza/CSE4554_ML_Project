    def __init__(self, module):
        super(SelfSignedCertificate, self).__init__(module)
        self.notBefore = module.params['selfsigned_notBefore']
        self.notAfter = module.params['selfsigned_notAfter']
        self.digest = module.params['selfsigned_digest']
        self.version = module.params['selfsigned_version']
        self.serial_number = randint(1000, 99999)
        self.csr = crypto_utils.load_certificate_request(self.csr_path)
        self.privatekey = crypto_utils.load_privatekey(
            self.privatekey_path, self.privatekey_passphrase
        )