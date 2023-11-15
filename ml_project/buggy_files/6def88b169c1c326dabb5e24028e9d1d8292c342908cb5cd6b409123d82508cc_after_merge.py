    def __init__(self, wallet_dir):
        super(BitcoinWallet, self).__init__()

        if self.TESTNET:
            bitcoin.set_testnet()
            network.set_testnet()

        self.wallet_dir = wallet_dir
        self.wallet_file = 'tbtc_wallet' if self.TESTNET else 'btc_wallet'
        self.min_confirmations = 0
        self.daemon = None
        self.wallet_password = None
        self.storage = None
        self.wallet = None

        self.initialize_storage(self.wallet_dir, self.wallet_file)
        if self.created:
            # If the wallet has been created already, we try to unlock it.
            self.unlock_wallet()