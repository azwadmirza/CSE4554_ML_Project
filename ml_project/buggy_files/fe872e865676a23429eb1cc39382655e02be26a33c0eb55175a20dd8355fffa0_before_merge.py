    async def is_alias(
        self, guild: discord.Guild, alias_name: str, server_aliases: Iterable[AliasEntry] = ()
    ) -> (bool, AliasEntry):

        if not server_aliases:
            server_aliases = await self.unloaded_aliases(guild)

        global_aliases = await self.unloaded_global_aliases()

        for aliases in (server_aliases, global_aliases):
            for alias in aliases:
                if alias.name == alias_name:
                    return True, alias

        return False, None