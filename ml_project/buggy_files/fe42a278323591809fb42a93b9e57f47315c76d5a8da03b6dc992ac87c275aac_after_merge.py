    async def role(self, ctx: commands.Context, *, role_name: discord.Role):
        """Set the role to use for DJ mode."""
        await self.config.guild(ctx.guild).dj_role.set(role_name.id)
        self._dj_role_cache[ctx.guild.id] = role_name.id
        dj_role = self._dj_role_cache.setdefault(
            ctx.guild.id, await self.config.guild(ctx.guild).dj_role()
        )
        dj_role_obj = ctx.guild.get_role(dj_role)
        await self._embed_msg(
            ctx,
            title=_("Settings Changed"),
            description=_("DJ role set to: {role.name}.").format(role=dj_role_obj),
        )