    def initiate_payment(
        self,
        registry_address: TokenNetworkRegistryAddress,
        token_address: TokenAddress,
        target_address: TargetAddress,
        amount: PaymentAmount,
        identifier: PaymentID,
        secret: Secret,
        secret_hash: SecretHash,
        lock_timeout: BlockTimeout,
    ) -> Response:
        log.debug(
            "Initiating payment",
            node=to_checksum_address(self.raiden_api.address),
            registry_address=to_checksum_address(registry_address),
            token_address=to_checksum_address(token_address),
            target_address=to_checksum_address(target_address),
            amount=amount,
            payment_identifier=identifier,
            secret=secret,
            secret_hash=secret_hash,
            lock_timeout=lock_timeout,
        )

        if identifier is None:
            identifier = create_default_identifier()

        try:
            payment_status = self.raiden_api.transfer(
                registry_address=registry_address,
                token_address=token_address,
                target=target_address,
                amount=amount,
                identifier=identifier,
                secret=secret,
                secrethash=secret_hash,
                lock_timeout=lock_timeout,
            )
        except (
            InvalidAmount,
            InvalidBinaryAddress,
            InvalidSecret,
            InvalidSecretHash,
            InvalidPaymentIdentifier,
            PaymentConflict,
            UnknownTokenAddress,
        ) as e:
            return api_error(errors=str(e), status_code=HTTPStatus.CONFLICT)
        except InsufficientFunds as e:
            return api_error(errors=str(e), status_code=HTTPStatus.PAYMENT_REQUIRED)

        result = payment_status.payment_done.get()

        if isinstance(result, EventPaymentSentFailed):
            return api_error(
                errors=f"Payment couldn't be completed because: {result.reason}",
                status_code=HTTPStatus.CONFLICT,
            )

        assert isinstance(result, EventPaymentSentSuccess)
        payment = {
            "initiator_address": self.raiden_api.address,
            "registry_address": registry_address,
            "token_address": token_address,
            "target_address": target_address,
            "amount": amount,
            "identifier": identifier,
            "secret": result.secret,
            "secret_hash": sha256(result.secret).digest(),
        }
        result = self.payment_schema.dump(payment)
        return api_response(result=result)