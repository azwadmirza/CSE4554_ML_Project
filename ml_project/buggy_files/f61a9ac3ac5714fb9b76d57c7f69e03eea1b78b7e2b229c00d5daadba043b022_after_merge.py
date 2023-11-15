    async def localwhitelist_remove(
        self,
        ctx: commands.Context,
        *users_or_roles: List[Union[discord.Member, discord.Role, int]],
    ):
        """
        Removes user or role from whitelist.
        """
        names = [getattr(users_or_roles, "name", users_or_roles) for u_or_r in users_or_roles]
        uids = [getattr(users_or_roles, "id", users_or_roles) for u_or_r in users_or_roles]
        await self.bot._whiteblacklist_cache.remove_from_whitelist(ctx.guild, uids)

        await ctx.send(
            _("{names} removed from the local whitelist.").format(names=humanize_list(names))
        )