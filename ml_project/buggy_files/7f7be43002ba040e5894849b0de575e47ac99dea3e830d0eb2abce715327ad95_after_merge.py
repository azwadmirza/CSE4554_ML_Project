    def __init__(self,
                 wallet,
                 schedule,
                 order_chooser=weighted_order_choose,
                 sign_method=None,
                 callbacks=None,
                 tdestaddrs=None,
                 ignored_makers=None):
        """Schedule must be a list of tuples: (see sample_schedule_for_testnet
        for explanation of syntax, also schedule.py module in this directory),
        which will be a sequence of joins to do.
        Callbacks:
        External callers set the 3 callbacks for filtering orders,
        sending info messages to client, and action on completion.
        "None" is allowable for taker_info_callback, defaults to log msg.
        Callback function definitions:
        =====================
        filter_orders_callback
        =====================
        args:
        1. orders_fees - a list of two items 1. orders dict 2 total cjfee
        2. cjamount - coinjoin amount in satoshis
        returns:
        False - offers rejected OR
        True - offers accepted OR
        'retry' - offers not accepted but try again
        =======================
        on_finished_callback
        =======================
        args:
        1. res - True means tx successful, False means tx unsucessful
        2. fromtx - True means not the final transaction, False means final
         (end of schedule), 'unconfirmed' means tx seen on the network only.
        3. waittime - passed in minutes, time to wait after confirmation before
         continuing to next tx (thus, only used if fromtx is True).
        4. txdetails - a tuple (txd, txid) - only to be used when fromtx
         is 'unconfirmed', used for monitoring.
        returns:
        None
        ========================
        taker_info_callback
        ========================
        args:
        1. type - one of 'ABORT' or 'INFO', the former signals the client that
         processing of this transaction is aborted, the latter is only an update.
        2. message - an information message.
        returns:
        None
        """
        self.aborted = False
        self.wallet = wallet
        self.schedule = schedule
        self.order_chooser = order_chooser

        #List (which persists between transactions) of makers
        #who have not responded or behaved maliciously at any
        #stage of the protocol.
        self.ignored_makers = [] if not ignored_makers else ignored_makers

        #Used in attempts to complete with subset after second round failure:
        self.honest_makers = []
        #Toggle: if set, only honest makers will be used from orderbook
        self.honest_only = False

        #Temporary (per transaction) list of makers that keeps track of
        #which have responded, both in Stage 1 and Stage 2. Before each
        #stage, the list is set to the full set of expected responders,
        #and entries are removed when honest responses are received;
        #emptiness of the list can be used to trigger completion of
        #processing.
        self.nonrespondants = []

        self.waiting_for_conf = False
        self.txid = None
        self.schedule_index = -1
        self.tdestaddrs = [] if not tdestaddrs else tdestaddrs
        #allow custom wallet-based clients to use their own signing code;
        #currently only setting "wallet" is allowed, calls wallet.sign_tx(tx)
        self.sign_method = sign_method
        self.filter_orders_callback = callbacks[0]
        self.taker_info_callback = callbacks[1]
        if not self.taker_info_callback:
            self.taker_info_callback = self.default_taker_info_callback
        self.on_finished_callback = callbacks[2]