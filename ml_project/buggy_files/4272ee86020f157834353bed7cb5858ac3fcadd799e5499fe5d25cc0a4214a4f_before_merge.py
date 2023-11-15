    async def localblacklist_add(
        self, ctx: commands.Context, *, user_or_role: Union[discord.Member, discord.Role, int]
    ):
        """
        Adds a user or role to the blacklist.
        """
        user = isinstance(user_or_role, discord.Member)
        if isinstance(user_or_role, int):
            user_or_role = discord.Object(id=user_or_role)
            user = True

        if user:
            if user_or_role.id == ctx.author.id:
                await ctx.send(_("You cannot blacklist yourself!"))
                return
            if user_or_role.id == ctx.guild.owner_id and not await ctx.bot.is_owner(ctx.author):
                await ctx.send(_("You cannot blacklist the guild owner!"))
                return
            if await ctx.bot.is_owner(user_or_role):
                await ctx.send(_("You cannot blacklist a bot owner!"))
                return

        async with ctx.bot._config.guild(ctx.guild).blacklist() as curr_list:
            if user_or_role.id not in curr_list:
                curr_list.append(user_or_role.id)

        if user:
            await ctx.send(_("User added to blacklist."))
        else:
            await ctx.send(_("Role added to blacklist."))