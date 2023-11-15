    async def localwhitelist_add(
        self,
        ctx: commands.Context,
        *users_or_roles: List[Union[discord.Member, discord.Role, int]],
    ):
        """
        Adds a user or role to the whitelist.
        """
        names = [getattr(users_or_roles, "name", users_or_roles) for u_or_r in users_or_roles]
        uids = [getattr(users_or_roles, "id", users_or_roles) for u_or_r in users_or_roles]
        await self.bot._whiteblacklist_cache.add_to_whitelist(ctx.guild, uids)

        await ctx.send(_("{names} added to whitelist.").format(names=humanize_list(names)))