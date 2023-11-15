    def sanitize_output(ctx: commands.Context, keys: dict, input_: str) -> str:
        """Hides the bot's token from a string."""
        token = ctx.bot.http.token
        r = "[EXPUNGED]"
        result = input_.replace(token, r)
        result = result.replace(token.lower(), r)
        result = result.replace(token.upper(), r)
        for provider, data in keys.items():
            for name, key in data.items():
                result = result.replace(key, r)
                result = result.replace(key.upper(), r)
                result = result.replace(key.lower(), r)
        return result