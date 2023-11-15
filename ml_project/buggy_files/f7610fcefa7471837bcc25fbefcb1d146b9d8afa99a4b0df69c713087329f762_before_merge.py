    async def api(self, ctx: commands.Context, service: str, *, tokens: TokenConverter):
        """Set various external API tokens.
        
        This setting will be asked for by some 3rd party cogs and some core cogs.

        To add the keys provide the service name and the tokens as a comma separated
        list of key,values as described by the cog requesting this command.

        Note: API tokens are sensitive and should only be used in a private channel
        or in DM with the bot.
        """
        if ctx.channel.permissions_for(ctx.me).manage_messages:
            await ctx.message.delete()
        await ctx.bot._config.api_tokens.set_raw(service, value=tokens)
        await ctx.send(_("`{service}` API tokens have been set.").format(service=service))