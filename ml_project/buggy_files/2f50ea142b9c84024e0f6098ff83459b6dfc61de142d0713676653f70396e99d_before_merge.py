    async def announcer(self):
        guild_list = self.ctx.bot.guilds
        bot_owner = (await self.ctx.bot.application_info()).owner
        for g in guild_list:
            if not self.active:
                return

            if await self.config.guild(g).announce_ignore():
                continue

            channel = await self._get_announce_channel(g)

            try:
                await channel.send(self.message)
            except discord.Forbidden:
                await bot_owner.send(
                    _("I could not announce to server: {server.id}").format(server=g)
                )
            await asyncio.sleep(0.5)

        self.active = False