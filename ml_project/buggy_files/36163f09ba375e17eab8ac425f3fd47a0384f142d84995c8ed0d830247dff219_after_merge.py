    async def _maybe_update_config(self):
        """Maybe update `delete_delay` value set by Config prior to Mod 1.0.0."""
        if not await self.settings.version():
            guild_dict = await self.settings.all_guilds()
            for guild_id, info in guild_dict.items():
                delete_repeats = info.get("delete_repeats", False)
                if delete_repeats:
                    val = 3
                else:
                    val = -1
                await self.settings.guild(discord.Object(id=guild_id)).delete_repeats.set(val)
            await self.settings.version.set("1.0.0")  # set version of last update
        if await self.settings.version() < "1.1.0":
            prefixes = await self.bot.get_valid_prefixes()
            msg = _(
                "Ignored guilds and channels have been moved. "
                "Please use `{prefix}moveignoredchannels` if "
                "you were previously using these functions."
            ).format(prefix=prefixes[0])
            await self.bot.send_to_owners(msg)
            await self.settings.version.set(__version__)