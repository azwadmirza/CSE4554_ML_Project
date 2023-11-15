    def __init__(self, d):
        Xpub.__init__(self, derivation_prefix=d.get('derivation'), root_fingerprint=d.get('root_fingerprint'))
        KeyStore.__init__(self)
        # Errors and other user interaction is done through the wallet's
        # handler.  The handler is per-window and preserved across
        # device reconnects
        self.xpub = d.get('xpub')
        self.label = d.get('label')
        self.soft_device_id = d.get('soft_device_id')  # type: Optional[str]
        self.handler = None  # type: Optional[HardwareHandlerBase]
        run_hook('init_keystore', self)