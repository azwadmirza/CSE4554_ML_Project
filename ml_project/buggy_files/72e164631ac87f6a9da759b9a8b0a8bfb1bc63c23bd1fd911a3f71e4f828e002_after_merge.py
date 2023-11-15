    def __init__(self, wallet_service):
        self.active_orders = {}
        assert isinstance(wallet_service, WalletService)
        self.wallet_service = wallet_service
        self.nextoid = -1
        self.offerlist = None
        self.sync_wait_loop = task.LoopingCall(self.try_to_create_my_orders)
        self.sync_wait_loop.start(2.0, now=False)
        self.aborted = False