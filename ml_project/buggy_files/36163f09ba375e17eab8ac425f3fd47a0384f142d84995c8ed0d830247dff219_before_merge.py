    async def _maybe_update_config(self):
        """Maybe update `delete_delay` value set by Config prior to Mod 1.0.0."""
        if await self.settings.version():
            return
        guild_dict = await self.settings.all_guilds()
        for guild_id, info in guild_dict.items():
            delete_repeats = info.get("delete_repeats", False)
            if delete_repeats:
                val = 3
            else:
                val = -1
            await self.settings.guild(discord.Object(id=guild_id)).delete_repeats.set(val)
        await self.settings.version.set(__version__)