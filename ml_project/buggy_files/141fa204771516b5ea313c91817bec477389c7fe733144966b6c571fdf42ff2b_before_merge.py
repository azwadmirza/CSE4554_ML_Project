    def __init__(self, wallet):
        # The two principal member variables
        # are the blockchaininterface instance,
        # which is currently global in JM but
        # could be more flexible in future, and
        # the JM wallet object.
        self.bci = jm_single().bc_interface

        # main loop used to check for transactions, instantiated
        # after wallet is synced:
        self.monitor_loop = None
        self.wallet = wallet
        self.synced = False

        # keep track of the quasi-real-time blockheight
        # (updated in main monitor loop)
        self.current_blockheight = None
        if self.bci is not None:
            if not self.update_blockheight():
                # this accounts for the unusual case
                # where the application started up with
                # a functioning blockchain interface, but
                # that bci is now failing when we are starting
                # the wallet service.
                raise Exception("WalletService failed to start "
                                "due to inability to query block height.")
        else:
            jlog.warning("No blockchain source available, " +
                "wallet tools will not show correct balances.")

        # Dicts of registered callbacks, by type
        # and then by txinfo, for events
        # on transactions.
        self.callbacks = {}
        self.callbacks["all"] = []
        self.callbacks["unconfirmed"] = {}
        self.callbacks["confirmed"] = {}

        self.restart_callback = None

        # transactions we are actively monitoring,
        # i.e. they are not new but we want to track:
        self.active_txids = []
        # to ensure transactions are only processed once:
        self.processed_txids = []

        self.set_autofreeze_warning_cb()