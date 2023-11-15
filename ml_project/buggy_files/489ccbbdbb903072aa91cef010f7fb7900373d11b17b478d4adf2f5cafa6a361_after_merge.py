    def initialize(self, orderbook):
        """Once the daemon is active and has returned the current orderbook,
        select offers, re-initialize variables and prepare a commitment,
        then send it to the protocol to fill offers.
        """
        if self.aborted:
            return (False,)
        self.taker_info_callback("INFO", "Received offers from joinmarket pit")
        #choose the next item in the schedule
        self.schedule_index += 1
        if self.schedule_index == len(self.schedule):
            self.taker_info_callback("INFO", "Finished all scheduled transactions")
            self.on_finished_callback(True)
            return (False,)
        else:
            #read the settings from the schedule entry
            si = self.schedule[self.schedule_index]
            self.mixdepth = si[0]
            self.cjamount = si[1]
            #non-integer coinjoin amounts are treated as fractions
            #this is currently used by the tumbler algo
            if isinstance(self.cjamount, float):
                #the mixdepth balance is fixed at the *start* of each new
                #mixdepth in tumble schedules:
                if self.schedule_index == 0 or si[0] != self.schedule[
                    self.schedule_index - 1]:
                    self.mixdepthbal = self.wallet.get_balance_by_mixdepth(
                        )[self.mixdepth]
                #reset to satoshis
                self.cjamount = int(self.cjamount * self.mixdepthbal)
                if self.cjamount < jm_single().mincjamount:
                    jlog.info("Coinjoin amount too low, bringing up to: " + str(
                        jm_single().mincjamount))
                    self.cjamount = jm_single().mincjamount
            self.n_counterparties = si[2]
            self.my_cj_addr = si[3]
            #if destination is flagged "INTERNAL", choose a destination
            #from the next mixdepth modulo the maxmixdepth
            if self.my_cj_addr == "INTERNAL":
                next_mixdepth = (self.mixdepth + 1) % self.wallet.max_mix_depth
                jlog.info("Choosing a destination from mixdepth: " + str(next_mixdepth))
                self.my_cj_addr = self.wallet.get_internal_addr(next_mixdepth)
                jlog.info("Chose destination address: " + self.my_cj_addr)
            self.outputs = []
            self.cjfee_total = 0
            self.maker_txfee_contributions = 0
            self.txfee_default = 5000
            self.latest_tx = None
            self.txid = None

        sweep = True if self.cjamount == 0 else False
        if not self.filter_orderbook(orderbook, sweep):
            return (False,)
        #choose coins to spend
        self.taker_info_callback("INFO", "Preparing bitcoin data..")
        if not self.prepare_my_bitcoin_data():
            return (False,)
        #Prepare a commitment
        commitment, revelation, errmsg = self.make_commitment()
        if not commitment:
            utxo_pairs, to, ts = revelation
            if len(to) == 0:
                #If any utxos are too new, then we can continue retrying
                #until they get old enough; otherwise, we have to abort
                #(TODO, it's possible for user to dynamically add more coins,
                #consider if this option means we should stay alive).
                self.taker_info_callback("ABORT", errmsg)
                self.on_finished_callback(False)
            else:
                self.taker_info_callback("INFO", errmsg)
            return (False,)
        else:
            self.taker_info_callback("INFO", errmsg)

        #Initialization has been successful. We must set the nonrespondants
        #now to keep track of what changed when we receive the utxo data
        self.nonrespondants = self.orderbook.keys()

        return (True, self.cjamount, commitment, revelation, self.orderbook)