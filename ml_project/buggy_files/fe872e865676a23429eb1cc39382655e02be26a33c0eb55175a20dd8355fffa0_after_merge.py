    async def is_alias(
        self,
        guild: Optional[discord.Guild],
        alias_name: str,
        server_aliases: Iterable[AliasEntry] = (),
    ) -> Tuple[bool, Optional[AliasEntry]]:

        if not server_aliases and guild is not None:
            server_aliases = await self.unloaded_aliases(guild)

        global_aliases = await self.unloaded_global_aliases()

        for aliases in (server_aliases, global_aliases):
            for alias in aliases:
                if alias.name == alias_name:
                    return True, alias

        return False, None