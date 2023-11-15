    def _worker_is_bonded_to_staker(self, registry: BaseContractRegistry) -> bool:
        """
        This method assumes the stamp's signature is valid and accurate.
        As a follow-up, this checks that the worker is linked to a staker, but it may be
        the case that the "staker" isn't "staking" (e.g., all her tokens have been slashed).
        """
        # Lazy agent get or create
        staking_agent = ContractAgency.get_agent(StakingEscrowAgent, registry=registry)

        staker_address = staking_agent.get_staker_from_worker(worker_address=self.worker_address)
        if staker_address == BlockchainInterface.NULL_ADDRESS:
            raise self.DetachedWorker(f"Worker {self.worker_address} is detached")
        return staker_address == self.checksum_address