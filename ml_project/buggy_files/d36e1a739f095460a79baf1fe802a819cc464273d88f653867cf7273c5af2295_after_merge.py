    def block_until_ready(self, poll_rate: int = None, timeout: int = None):
        """
        Polls the staking_agent and blocks until the staking address is not
        a null address for the given worker_address. Once the worker is bonded, it returns the staker address.
        """
        if not self.__worker_address:
            raise RuntimeError("No worker address available")

        timeout = timeout or self.BONDING_TIMEOUT
        poll_rate = poll_rate or self.BONDING_POLL_RATE
        staking_agent = ContractAgency.get_agent(StakingEscrowAgent, registry=self.registry)
        client = staking_agent.blockchain.client
        start = maya.now()

        emitter = StdoutEmitter()  # TODO: Make injectable, or embed this logic into Ursula
        emitter.message("Waiting for bonding and funding...", color='yellow')

        funded, bonded = False, False
        while True:

            # Read
            staking_address = staking_agent.get_staker_from_worker(self.__worker_address)
            ether_balance = client.get_balance(self.__worker_address)

            # Bonding
            if (not bonded) and (staking_address != BlockchainInterface.NULL_ADDRESS):
                bonded = True
                emitter.message(f"Worker is bonded to ({staking_address})!", color='green', bold=True)

            # Balance
            if ether_balance and (not funded):
                funded, balance = True, Web3.fromWei(ether_balance, 'ether')
                emitter.message(f"Worker is funded with {balance} ETH!", color='green', bold=True)

            # Success and Escape
            if staking_address != BlockchainInterface.NULL_ADDRESS and ether_balance:
                self._checksum_address = staking_address

                # TODO: #1823 - Workaround for new nickname every restart
                self.nickname, self.nickname_metadata = nickname_from_seed(self.checksum_address)
                break

            # Crash on Timeout
            if timeout:
                now = maya.now()
                delta = now - start
                if delta.total_seconds() >= timeout:
                    if staking_address == BlockchainInterface.NULL_ADDRESS:
                        raise self.DetachedWorker(f"Worker {self.__worker_address} not bonded after waiting {timeout} seconds.")
                    elif not ether_balance:
                        raise RuntimeError(f"Worker {self.__worker_address} has no ether after waiting {timeout} seconds.")

            # Increment
            time.sleep(poll_rate)