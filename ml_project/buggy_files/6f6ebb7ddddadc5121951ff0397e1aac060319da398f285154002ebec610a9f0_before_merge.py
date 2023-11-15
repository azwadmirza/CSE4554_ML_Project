    def transfer_async(
        self,
        registry_address: TokenNetworkRegistryAddress,
        token_address: TokenAddress,
        amount: PaymentAmount,
        target: TargetAddress,
        identifier: PaymentID = None,
        secret: Secret = None,
        secrethash: SecretHash = None,
        lock_timeout: BlockTimeout = None,
    ) -> "PaymentStatus":
        current_state = views.state_from_raiden(self.raiden)
        token_network_registry_address = self.raiden.default_registry.address

        if not isinstance(amount, int):  # pragma: no unittest
            raise InvalidAmount("Amount not a number")

        if amount <= 0:
            raise InvalidAmount("Amount negative")

        if amount > UINT256_MAX:
            raise InvalidAmount("Amount too large")

        if not is_binary_address(token_address):
            raise InvalidBinaryAddress("token address is not valid.")

        if token_address not in views.get_token_identifiers(current_state, registry_address):
            raise UnknownTokenAddress("Token address is not known.")

        if not is_binary_address(target):
            raise InvalidBinaryAddress("target address is not valid.")

        valid_tokens = views.get_token_identifiers(
            views.state_from_raiden(self.raiden), registry_address
        )
        if token_address not in valid_tokens:
            raise UnknownTokenAddress("Token address is not known.")

        if secret is not None and not isinstance(secret, T_Secret):
            raise InvalidSecret("secret is not valid.")

        if secrethash is not None and not isinstance(secrethash, T_SecretHash):
            raise InvalidSecretHash("secrethash is not valid.")

        if identifier is None:
            identifier = create_default_identifier()

        if identifier <= 0:
            raise InvalidPaymentIdentifier("Payment identifier cannot be 0 or negative")

        if identifier > UINT64_MAX:
            raise InvalidPaymentIdentifier("Payment identifier is too large")

        log.debug(
            "Initiating transfer",
            initiator=to_checksum_address(self.raiden.address),
            target=to_checksum_address(target),
            token=to_checksum_address(token_address),
            amount=amount,
            identifier=identifier,
        )

        token_network_address = views.get_token_network_address_by_token_address(
            chain_state=current_state,
            token_network_registry_address=token_network_registry_address,
            token_address=token_address,
        )

        if token_network_address is None:
            raise UnknownTokenAddress(
                f"Token {to_checksum_address(token_address)} is not registered "
                f"with the network {to_checksum_address(registry_address)}."
            )

        payment_status = self.raiden.mediated_transfer_async(
            token_network_address=token_network_address,
            amount=amount,
            target=target,
            identifier=identifier,
            secret=secret,
            secrethash=secrethash,
            lock_timeout=lock_timeout,
        )
        return payment_status