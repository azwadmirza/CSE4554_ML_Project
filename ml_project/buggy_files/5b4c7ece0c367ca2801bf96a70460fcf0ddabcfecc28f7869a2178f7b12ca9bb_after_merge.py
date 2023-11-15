    async def _check_token(token: MutableMapping):
        now = int(time.time())
        return token["expires_at"] - now < 60