    async def _status_check(self, track, playing_servers):
        if playing_servers == 0:
            await self.bot.change_presence(activity=None)
        elif playing_servers == 1:
            await self.bot.change_presence(
                activity=discord.Activity(name=track, type=discord.ActivityType.listening)
            )
        elif playing_servers > 1:
            await self.bot.change_presence(
                activity=discord.Activity(
                    name=_("music in {} servers").format(playing_servers),
                    type=discord.ActivityType.playing,
                )
            )