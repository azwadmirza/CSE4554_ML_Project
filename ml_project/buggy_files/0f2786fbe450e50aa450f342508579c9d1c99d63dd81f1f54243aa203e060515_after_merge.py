    def __init__(self,
                 checksum_address: str,
                 is_transacting: bool = True,
                 client_password: str = None,
                 *args, **kwargs):
        super().__init__(checksum_address=checksum_address, *args, **kwargs)
        self.worklock_agent = ContractAgency.get_agent(WorkLockAgent, registry=self.registry)
        self.staking_agent = ContractAgency.get_agent(StakingEscrowAgent, registry=self.registry)
        self.economics = EconomicsFactory.get_economics(registry=self.registry)

        if is_transacting:
            self.transacting_power = TransactingPower(password=client_password, account=checksum_address)
            self.transacting_power.activate()