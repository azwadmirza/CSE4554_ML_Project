    def __init__(self, wallet_dir):
        super(BitcoinWallet, self).__init__()

        bitcoinlib_main.initialize_lib(wallet_dir)
        from bitcoinlib.wallets import wallet_exists, HDWallet

        self.network = 'testnet' if self.TESTNET else 'bitcoin'
        self.wallet_dir = wallet_dir
        self.min_confirmations = 0
        self.wallet = None
        self.unlocked = True
        self.db_path = os.path.join(wallet_dir, 'wallets.sqlite')
        self.wallet_name = 'tribler_testnet' if self.TESTNET else 'tribler'

        if wallet_exists(self.wallet_name, databasefile=self.db_path):
            self.wallet = HDWallet(self.wallet_name, databasefile=self.db_path)
            self.created = True