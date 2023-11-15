    async def _check_token(token: dict):
        now = int(time.time())
        return token["expires_at"] - now < 60