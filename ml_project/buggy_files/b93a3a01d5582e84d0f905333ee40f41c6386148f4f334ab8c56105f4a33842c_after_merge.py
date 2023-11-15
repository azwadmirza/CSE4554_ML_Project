    async def after(self, ctx: commands.Context, message_id: int, delete_pinned: bool = False):
        """Delete all messages after a specified message.

        To get a message id, enable developer mode in Discord's
        settings, 'appearance' tab. Then right click a message
        and copy its id.
        """

        channel = ctx.channel
        author = ctx.author

        try:
            after = await channel.get_message(message_id)
        except discord.NotFound:
            return await ctx.send(_("Message not found."))

        to_delete = await self.get_messages_for_deletion(
            channel=channel, number=None, after=after, delete_pinned=delete_pinned
        )

        reason = "{}({}) deleted {} messages in channel {}.".format(
            author.name, author.id, len(to_delete), channel.name
        )
        log.info(reason)

        await mass_purge(to_delete, channel)