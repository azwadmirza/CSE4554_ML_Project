    async def warn(self, ctx: commands.Context, user: discord.Member, reason: str):
        """Warn the user for the specified reason

        Reason must be a registered reason, or "custom" if custom reasons are allowed
        """
        if reason.lower() == "custom":
            custom_allowed = await self.config.guild(ctx.guild).allow_custom_reasons()
            if not custom_allowed:
                await ctx.send(
                    _(
                        "Custom reasons are not allowed! Please see {} for "
                        "a complete list of valid reasons"
                    ).format("`{}reasonlist`".format(ctx.prefix))
                )
                return
            reason_type = await self.custom_warning_reason(ctx)
        else:
            guild_settings = self.config.guild(ctx.guild)
            async with guild_settings.reasons() as registered_reasons:
                if reason.lower() not in registered_reasons:
                    await ctx.send(_("That is not a registered reason!"))
                    return
                else:
                    reason_type = registered_reasons[reason.lower()]

        member_settings = self.config.member(user)
        current_point_count = await member_settings.total_points()
        warning_to_add = {
            str(ctx.message.id): {
                "points": reason_type["points"],
                "description": reason_type["description"],
                "mod": ctx.author.id,
            }
        }
        async with member_settings.warnings() as user_warnings:
            user_warnings.update(warning_to_add)
        current_point_count += reason_type["points"]
        await member_settings.total_points.set(current_point_count)

        await warning_points_add_check(self.config, ctx, user, current_point_count)
        await ctx.tick()