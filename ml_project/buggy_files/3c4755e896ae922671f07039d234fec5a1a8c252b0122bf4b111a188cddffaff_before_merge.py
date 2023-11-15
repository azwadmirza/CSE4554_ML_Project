    async def _get_auth(self):
        if self.client_id is None or self.client_secret is None:
            tokens = await self.bot.get_shared_api_tokens("spotify")
            self.client_id = tokens.get("client_id", "")
            self.client_secret = tokens.get("client_secret", "")