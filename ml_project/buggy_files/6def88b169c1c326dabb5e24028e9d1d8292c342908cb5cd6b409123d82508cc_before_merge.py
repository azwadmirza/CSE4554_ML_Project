    def __init__(self, wallet_dir):
        super(BitcoinWallet, self).__init__()

        if self.TESTNET:
            bitcoin.set_testnet()
            network.set_testnet()

        self.wallet_dir = wallet_dir
        self.wallet_file = 'tbtc_wallet' if self.TESTNET else 'btc_wallet'
        self.min_confirmations = 0
        self.created = False
        self.daemon = None
        keychain_pw = self.get_wallet_password()
        self.wallet_password = keychain_pw if keychain_pw else None  # Convert empty passwords to None
        self.storage = None
        self.wallet = None
        self.load_wallet(self.wallet_dir, self.wallet_file)