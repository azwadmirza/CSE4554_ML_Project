    async def response(self, ctx, ticket_number: int):
        """
        Open a message tunnel.
        
        This tunnel will forward things you say in this channel
        to the ticket opener's direct messages.

        Tunnels do not persist across bot restarts.
        """

        # note, mod_or_permissions is an implicit guild_only
        guild = ctx.guild
        rec = await self.config.custom("REPORT", guild.id, ticket_number).report()

        try:
            user = guild.get_member(rec.get("user_id"))
        except KeyError:
            return await ctx.send(_("That ticket doesn't seem to exist"))

        if user is None:
            return await ctx.send(_("That user isn't here anymore."))

        tun = Tunnel(recipient=user, origin=ctx.channel, sender=ctx.author)

        if tun is None:
            return await ctx.send(
                _(
                    "Either you or the user you are trying to reach already "
                    "has an open communication."
                )
            )

        big_topic = _(
            "{who} opened a 2-way communication "
            "about ticket number {ticketnum}. Anything you say or upload here "
            "(8MB file size limitation on uploads) "
            "will be forwarded to them until the communication is closed.\n"
            "You can close a communication at any point by reacting with "
            "the \N{NEGATIVE SQUARED CROSS MARK} to the last message recieved.\n"
            "Any message succesfully forwarded will be marked with "
            "\N{WHITE HEAVY CHECK MARK}.\n"
            "Tunnels are not persistent across bot restarts."
        )
        topic = big_topic.format(
            ticketnum=ticket_number, who=_("A moderator in `{guild.name}` has").format(guild=guild)
        )
        try:
            m = await tun.communicate(message=ctx.message, topic=topic, skip_message_content=True)
        except discord.Forbidden:
            await ctx.send(_("That user has DMs disabled."))
        else:
            self.tunnel_store[(guild, ticket_number)] = {"tun": tun, "msgs": m}
            await ctx.send(big_topic.format(who=_("You have"), ticketnum=ticket_number))