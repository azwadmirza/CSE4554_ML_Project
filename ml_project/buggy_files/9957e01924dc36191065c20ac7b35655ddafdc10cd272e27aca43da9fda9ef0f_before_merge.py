        async def _status_check(playing_servers):
            if playing_servers == 0:
                await self.bot.change_presence(activity=None)
            if playing_servers == 1:
                single_title = await _players_check()
                await self.bot.change_presence(
                    activity=discord.Activity(
                        name=single_title[0], type=discord.ActivityType.listening
                    )
                )
            if playing_servers > 1:
                await self.bot.change_presence(
                    activity=discord.Activity(
                        name=_("music in {} servers").format(playing_servers),
                        type=discord.ActivityType.playing,
                    )
                )