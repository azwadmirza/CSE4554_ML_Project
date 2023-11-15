    def __init__(self, tc_community):
        super(TrustchainWallet, self).__init__()

        self.tc_community = tc_community
        self.created = True
        self.unlocked = True
        self.check_negative_balance = False
        self.transaction_history = []