    async def _currency_check(self, ctx: commands.Context, jukebox_price: int):
        jukebox = await self.config.guild(ctx.guild).jukebox()
        if jukebox and not await self._can_instaskip(ctx, ctx.author):
            try:
                await bank.withdraw_credits(ctx.author, jukebox_price)
                return True
            except ValueError:
                credits_name = await bank.get_currency_name(ctx.guild)
                await self._embed_msg(
                    ctx,
                    _("Not enough {currency} ({required_credits} required).").format(
                        currency=credits_name, required_credits=humanize_number(jukebox_price)
                    ),
                )
                return False
        else:
            return True