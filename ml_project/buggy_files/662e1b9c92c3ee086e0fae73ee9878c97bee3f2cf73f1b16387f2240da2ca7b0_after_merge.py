    async def set_shared_api_tokens(self, service_name: str, **tokens: str):
        """
        Sets shared API tokens for a service

        In most cases, this should not be used. Users should instead be using the 
        ``set api`` command
    
        This will not clear existing values not specified.

        Parameters
        ----------
        service_name: str
            The service to set tokens for
        **tokens
            token_name -> token

        Examples
        --------
        Setting the api_key for youtube from a value in a variable ``my_key``

        >>> await ctx.bot.set_shared_api_tokens("youtube", api_key=my_key)
        """

        async with self._config.custom(SHARED_API_TOKENS, service_name).all() as group:
            group.update(tokens)