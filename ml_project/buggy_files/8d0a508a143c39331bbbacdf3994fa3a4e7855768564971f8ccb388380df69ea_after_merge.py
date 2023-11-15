    def __init__(self):
        super(BaseDummyWallet, self).__init__()

        self.balance = 1000
        self.created = True
        self.unlocked = True
        self.address = ''.join([choice(string.lowercase) for _ in xrange(10)])
        self.transaction_history = []