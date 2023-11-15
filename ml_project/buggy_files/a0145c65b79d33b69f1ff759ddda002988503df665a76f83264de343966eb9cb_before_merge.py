    def _staker_is_really_staking(self) -> bool:
        """
        This method assumes the stamp's signature is valid and accurate.
        As a follow-up, this checks that the staker is, indeed, staking.
        """
        locked_tokens = self.staking_agent.get_locked_tokens(staker_address=self.checksum_address)
        return locked_tokens > 0  # TODO: Consider min stake size #1115