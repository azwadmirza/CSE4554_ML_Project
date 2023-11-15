    def get(self, token_address: TokenAddress = None, target_address: Address = None) -> Response:
        kwargs = validate_query_params(self.get_schema)
        return self.rest_api.get_raiden_events_payment_history_with_timestamps(
            registry_address=self.rest_api.raiden_api.raiden.default_registry.address,
            token_address=token_address,
            target_address=target_address,
            **kwargs,
        )