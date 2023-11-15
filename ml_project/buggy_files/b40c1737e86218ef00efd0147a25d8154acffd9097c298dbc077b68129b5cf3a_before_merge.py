    def __init__(self, community, circuit_id, balance_future):
        super(BalanceRequestCache, self).__init__(community.request_cache, u"balance-request", circuit_id)
        self.circuit_id = circuit_id
        self.balance_future = balance_future