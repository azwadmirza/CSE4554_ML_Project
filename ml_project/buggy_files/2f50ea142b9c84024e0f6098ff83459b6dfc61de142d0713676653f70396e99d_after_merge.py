    async def announcer(self):
        guild_list = self.ctx.bot.guilds
        failed = []
        for g in guild_list:
            if not self.active:
                return

            if await self.config.guild(g).announce_ignore():
                continue

            channel = await self._get_announce_channel(g)

            try:
                await channel.send(self.message)
            except discord.Forbidden:
                failed.append(str(g.id))
            await asyncio.sleep(0.5)

        msg = (
            _("I could not announce to the following server: ")
            if len(failed) == 1
            else _("I could not announce to the following servers: ")
        )
        msg += humanize_list(tuple(map(inline, failed)))
        await self.ctx.bot.send_to_owners(msg)
        self.active = False