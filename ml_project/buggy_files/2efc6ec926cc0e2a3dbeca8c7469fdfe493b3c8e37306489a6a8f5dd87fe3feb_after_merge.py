    async def _has_dj_role(self, ctx: commands.Context, member: discord.Member):
        dj_role = self._dj_role_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_role()
        )
        dj_role_obj = ctx.guild.get_role(dj_role)
        return dj_role_obj in ctx.guild.get_member(member.id).roles