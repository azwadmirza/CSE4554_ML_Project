    async def _can_instaskip(self, ctx: commands.Context, member: discord.Member):

        dj_enabled = await self.config.guild(ctx.guild).dj_enabled()

        if member.bot:
            return True

        if member.id == ctx.guild.owner_id:
            return True

        if dj_enabled:
            if await self._has_dj_role(ctx, member):
                return True

        if await ctx.bot.is_owner(member):
            return True

        if await ctx.bot.is_mod(member):
            return True

        if await self._channel_check(ctx):
            return True

        return False