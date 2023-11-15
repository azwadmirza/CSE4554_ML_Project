    async def paydayamount(self, ctx: commands.Context, creds: int):
        """Set the amount earned each payday."""
        guild = ctx.guild
        if creds <= 0 or creds > bank.MAX_BALANCE:
            await ctx.send(_("Har har so funny."))
            return
        credits_name = await bank.get_currency_name(guild)
        if await bank.is_global():
            await self.config.PAYDAY_CREDITS.set(creds)
        else:
            await self.config.guild(guild).PAYDAY_CREDITS.set(creds)
        await ctx.send(
            _("Every payday will now give {num} {currency}.").format(
                num=creds, currency=credits_name
            )
        )