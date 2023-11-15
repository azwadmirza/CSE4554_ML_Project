    async def transfer(self, ctx: commands.Context, to: discord.Member, amount: int):
        """Transfer currency to other users."""
        from_ = ctx.author
        currency = await bank.get_currency_name(ctx.guild)

        try:
            await bank.transfer_credits(from_, to, amount)
        except ValueError as e:
            return await ctx.send(str(e))

        await ctx.send(
            _("{user} transferred {num} {currency} to {other_user}").format(
                user=from_.display_name, num=amount, currency=currency, other_user=to.display_name
            )
        )