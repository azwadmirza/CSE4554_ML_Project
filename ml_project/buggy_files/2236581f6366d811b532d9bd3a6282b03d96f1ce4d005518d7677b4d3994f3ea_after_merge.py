    def add_token(
        self,
        token_address: TokenAddress,
        channel_participant_deposit_limit: TokenAmount,
        token_network_deposit_limit: TokenAmount,
        given_block_identifier: BlockSpecification,
    ) -> TokenNetworkAddress:
        """
        Register token of `token_address` with the token network.
        The limits apply for version 0.13.0 and above of raiden-contracts,
        since instantiation also takes the limits as constructor arguments.
        """
        if given_block_identifier == "latest":
            raise ValueError(
                'Calling a proxy with "latest" is usually wrong because '
                "the result of the precondition check is not precisely predictable."
            )

        if token_address == NULL_ADDRESS_BYTES:
            raise InvalidTokenAddress("The call to register a token at 0x00..00 will fail.")

        if token_network_deposit_limit <= 0:
            raise InvalidTokenNetworkDepositLimit(
                f"Token network deposit limit must be larger than zero, "
                f"{token_network_deposit_limit} given."
            )

        if channel_participant_deposit_limit <= 0:
            raise InvalidTokenNetworkDepositLimit(
                f"Participant deposit limit must be larger than zero, "
                f"{channel_participant_deposit_limit} given"
            )

        if channel_participant_deposit_limit > token_network_deposit_limit:
            raise InvalidChannelParticipantDepositLimit(
                f"Participant deposit limit must be smaller than the network "
                f"deposit limit, {channel_participant_deposit_limit} is larger "
                f"than {token_network_deposit_limit}."
            )

        token_proxy = self.proxy_manager.token(token_address, given_block_identifier)
        try:
            token_supply = token_proxy.total_supply(block_identifier=given_block_identifier)
            already_registered = self.get_token_network(
                token_address=token_address, block_identifier=given_block_identifier
            )
            deprecation_executor = self.get_deprecation_executor(
                block_identifier=given_block_identifier
            )
            settlement_timeout_min = self.settlement_timeout_min(
                block_identifier=given_block_identifier
            )
            settlement_timeout_max = self.settlement_timeout_max(
                block_identifier=given_block_identifier
            )
            chain_id = self.get_chain_id(block_identifier=given_block_identifier)
            secret_registry_address = self.get_secret_registry_address(
                block_identifier=given_block_identifier
            )
            max_token_networks = self.get_max_token_networks(
                block_identifier=given_block_identifier
            )
            token_networks_created = self.get_token_network_created(
                block_identifier=given_block_identifier
            )
        except ValueError:
            # If `given_block_identifier` has been pruned the checks cannot be performed
            pass
        except BadFunctionCallOutput:
            raise_on_call_returned_empty(given_block_identifier)
        else:
            if token_networks_created >= max_token_networks:
                raise MaxTokenNetworkNumberReached(
                    f"Number of token networks will exceed the maximum of {max_token_networks}"
                )

            if token_supply is None:
                raise InvalidToken(
                    "Given token address does not follow the "
                    "ERC20 standard (missing `totalSupply()`)"
                )
            if already_registered:
                raise BrokenPreconditionError(
                    "The token is already registered in the TokenNetworkRegistry."
                )

            if deprecation_executor == NULL_ADDRESS_BYTES:
                raise BrokenPreconditionError(
                    "The deprecation executor property for the TokenNetworkRegistry is invalid."
                )

            if chain_id == 0:
                raise BrokenPreconditionError(
                    "The chain ID property for the TokenNetworkRegistry is invalid."
                )

            if chain_id != self.rpc_client.chain_id:
                raise BrokenPreconditionError(
                    f"The provided chain ID {chain_id} does not match the "
                    f"network Raiden is running on: {self.rpc_client.chain_id}."
                )

            if secret_registry_address == NULL_ADDRESS_BYTES:
                raise BrokenPreconditionError(
                    "The secret registry address for the token network is invalid."
                )

            if settlement_timeout_min == 0:
                raise BrokenPreconditionError(
                    "The minimum settlement timeout for the token network "
                    "should be larger than zero."
                )

            if settlement_timeout_max <= settlement_timeout_min:
                raise BrokenPreconditionError(
                    "The maximum settlement timeout for the token network "
                    "should be larger than the minimum settlement timeout."
                )

        log_details = {
            "node": to_checksum_address(self.node_address),
            "contract": to_checksum_address(self.address),
            "token_address": to_checksum_address(token_address),
            "given_block_identifier": format_block_id(given_block_identifier),
            "channel_participant_deposit_limit": channel_participant_deposit_limit,
            "token_network_deposit_limit": token_network_deposit_limit,
        }
        with log_transaction(log, "add_token", log_details):
            return self._add_token(
                token_address=token_address,
                channel_participant_deposit_limit=channel_participant_deposit_limit,
                token_network_deposit_limit=token_network_deposit_limit,
                log_details=log_details,
            )