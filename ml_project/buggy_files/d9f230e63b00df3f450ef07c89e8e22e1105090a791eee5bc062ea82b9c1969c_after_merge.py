    def __init__(self):
        QWidget.__init__(self)
        self.request_mgr = None
        self.initialized = False
        self.wallets_to_create = []
        self.wallets = None
        self.active_wallet = None
        self.dialog = None
        self.btc_module_available = False