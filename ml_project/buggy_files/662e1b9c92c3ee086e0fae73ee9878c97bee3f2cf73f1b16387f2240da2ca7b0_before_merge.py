    async def set_shared_api_tokens(self, service_name: str, **tokens: str):
        """
        Sets shared API tokens for a service

        In most cases, this should not be used. Users should instead be using the 
        ``set api`` command
    
        This will not clear existing values not specified.
        """

        async with self._config.api_tokens.get_attr(service_name)() as method_abuse:
            method_abuse.update(**tokens)