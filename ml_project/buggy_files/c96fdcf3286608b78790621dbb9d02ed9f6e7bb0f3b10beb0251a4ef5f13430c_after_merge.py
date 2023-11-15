    async def warn(
        self,
        ctx: commands.Context,
        user: discord.Member,
        points: Optional[int] = 1,
        *,
        reason: str,
    ):
        """Warn the user for the specified reason.

        `<points>` number of points the warning should be for. If no number is supplied
        1 point will be given. Pre-set warnings disregard this.
        `<reason>` can be a registered reason if it exists or a custom one
        is created by default.
        """
        channel = ctx.channel
        guild = ctx.guild
        if user == ctx.author:
            await ctx.send(_("You cannot warn yourself."))
            return
        if user.bot:
            await ctx.send(_("You cannot warn other bots."))
            return
        custom_allowed = await self.config.guild(ctx.guild).allow_custom_reasons()
        guild_settings = self.config.guild(ctx.guild)
        reason_type = None
        async with guild_settings.reasons() as registered_reasons:
            if reason.lower() not in registered_reasons:
                msg = _("That is not a registered reason!")
                if custom_allowed:
                    reason_type = {"description": reason, "points": points}
                elif (
                    ctx.guild.owner == ctx.author
                    or ctx.channel.permissions_for(ctx.author).administrator
                    or await ctx.bot.is_owner(ctx.author)
                ):
                    msg += " " + _(
                        "Do `{prefix}warningset allowcustomreasons true` to enable custom "
                        "reasons."
                    ).format(prefix=ctx.clean_prefix)
                    return await ctx.send(msg)
            else:
                reason_type = registered_reasons[reason.lower()]
        if reason_type is None:
            return
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
        dm = await self.config.guild(ctx.guild).toggle_dm()
        dm_failed = False
        if dm:
            em = discord.Embed(
                title=_("Warning from {user}").format(user=ctx.author),
                description=reason_type["description"],
            )
            em.add_field(name=_("Points"), value=str(reason_type["points"]))
            try:
                await user.send(
                    _("You have received a warning in {guild_name}.").format(
                        guild_name=ctx.guild.name
                    ),
                    embed=em,
                )
            except discord.HTTPException:
                dm_failed = True

        if dm_failed:
            await ctx.send(
                _(
                    "A warning for {user} has been issued,"
                    " but I wasn't able to send them a warn message."
                ).format(user=user.mention)
            )

        toggle_channel = await self.config.guild(guild).toggle_channel()
        if toggle_channel:
            em = discord.Embed(
                title=_("Warning from {user}").format(user=ctx.author),
                description=reason_type["description"],
            )
            em.add_field(name=_("Points"), value=str(reason_type["points"]))
            warn_channel = self.bot.get_channel(await self.config.guild(guild).warn_channel())
            if warn_channel:
                if channel.permissions_for(guild.me).send_messages:
                    with contextlib.suppress(discord.HTTPException):
                        await channel.send(
                            _("{user} has been warned.").format(user=user.mention), embed=em,
                        )

            if not dm_failed:
                if warn_channel:
                    await ctx.tick()
                else:
                    await ctx.send(
                        _("{user} has been warned.").format(user=user.mention), embed=em
                    )
        else:
            if not dm_failed:
                await ctx.tick()
        try:
            reason_msg = _(
                "{reason}\n\nUse `{prefix}unwarn {user} {message}` to remove this warning."
            ).format(
                reason=_("{description}\nPoints: {points}").format(
                    description=reason_type["description"], points=reason_type["points"]
                ),
                prefix=ctx.clean_prefix,
                user=user.id,
                message=ctx.message.id,
            )
            await modlog.create_case(
                self.bot,
                ctx.guild,
                ctx.message.created_at,
                "warning",
                user,
                ctx.message.author,
                reason_msg,
                until=None,
                channel=None,
            )
        except RuntimeError:
            pass