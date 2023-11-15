    async def jukebox(self, ctx: commands.Context, price: int):
        """Set a price for queueing tracks for non-mods, 0 to disable."""
        if price < 0:
            return await self._embed_msg(
                ctx, title=_("Invalid Price"), description=_("Price can't be less than zero.")
            )
        if price == 0:
            jukebox = False
            await self._embed_msg(
                ctx, title=_("Setting Changed"), description=_("Jukebox mode disabled.")
            )
        else:
            jukebox = True
            await self._embed_msg(
                ctx,
                title=_("Setting Changed"),
                description=_("Track queueing command price set to {price} {currency}.").format(
                    price=humanize_number(price), currency=await bank.get_currency_name(ctx.guild)
                ),
            )

        await self.config.guild(ctx.guild).jukebox_price.set(price)
        await self.config.guild(ctx.guild).jukebox.set(jukebox)