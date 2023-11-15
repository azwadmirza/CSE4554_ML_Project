    def __init__(self, options):
        self.options = options

        self.authenticator = None
        self.check_ignore = None
        self.check_tcp = None
        self.certstore = None
        self.clientcerts = None
        self.ssl_insecure = False
        self.openssl_verification_mode_server = None
        self.configure(options, set(options.keys()))
        options.changed.connect(self.configure)