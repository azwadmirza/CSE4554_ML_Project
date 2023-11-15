    async def get_shared_api_tokens(self, service_name: str) -> Dict[str, str]:
        """
        Gets the shared API tokens for a service

        Parameters
        ----------
        service_name: str

        Returns
        -------
        Dict[str, str]
            A Mapping of token names to tokens.
            This mapping exists because some services have multiple tokens.
        """
        return await self._config.api_tokens.get_raw(service_name, default={})