    def register_token(
        self, registry_address: TokenNetworkRegistryAddress, token_address: TokenAddress
    ) -> Response:
        if self.raiden_api.raiden.config.environment_type == Environment.PRODUCTION:
            return api_error(
                errors="Registering a new token is currently disabled in production mode",
                status_code=HTTPStatus.NOT_IMPLEMENTED,
            )

        conflict_exceptions = (
            AddressWithoutCode,
            AlreadyRegisteredTokenAddress,
            InvalidBinaryAddress,
            InvalidToken,
            InvalidTokenAddress,
            RaidenRecoverableError,
        )
        log.debug(
            "Registering token",
            node=to_checksum_address(self.raiden_api.address),
            registry_address=to_checksum_address(registry_address),
            token_address=to_checksum_address(token_address),
        )
        try:
            token_network_address = self.raiden_api.token_network_register(
                registry_address=registry_address,
                token_address=token_address,
                channel_participant_deposit_limit=TokenAmount(UINT256_MAX),
                token_network_deposit_limit=TokenAmount(UINT256_MAX),
            )
        except conflict_exceptions as e:
            return api_error(errors=str(e), status_code=HTTPStatus.CONFLICT)
        except InsufficientEth as e:
            return api_error(errors=str(e), status_code=HTTPStatus.PAYMENT_REQUIRED)
        except MaxTokenNetworkNumberReached as e:
            return api_error(errors=str(e), status_code=HTTPStatus.FORBIDDEN)

        return api_response(
            result=dict(token_network_address=to_checksum_address(token_network_address)),
            status_code=HTTPStatus.CREATED,
        )