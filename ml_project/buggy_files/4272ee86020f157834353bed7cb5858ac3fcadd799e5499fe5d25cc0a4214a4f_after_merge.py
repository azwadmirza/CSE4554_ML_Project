    async def localblacklist_add(
        self,
        ctx: commands.Context,
        *users_or_roles: List[Union[discord.Member, discord.Role, int]],
    ):
        """
        Adds a user or role to the blacklist.
        """
        for user_or_role in users_or_roles:
            uid = discord.Object(id=getattr(user_or_role, "id", user_or_role))
            if uid.id == ctx.author.id:
                await ctx.send(_("You cannot blacklist yourself!"))
                return
            if uid.id == ctx.guild.owner_id and not await ctx.bot.is_owner(ctx.author):
                await ctx.send(_("You cannot blacklist the guild owner!"))
                return
            if await ctx.bot.is_owner(uid):
                await ctx.send(_("You cannot blacklist a bot owner!"))
                return
        names = [getattr(users_or_roles, "name", users_or_roles) for u_or_r in users_or_roles]
        uids = [getattr(users_or_roles, "id", users_or_roles) for u_or_r in users_or_roles]
        await self.bot._whiteblacklist_cache.add_to_blacklist(ctx.guild, uids)

        await ctx.send(
            _("{names} added to the local blacklist.").format(names=humanize_list(names))
        )