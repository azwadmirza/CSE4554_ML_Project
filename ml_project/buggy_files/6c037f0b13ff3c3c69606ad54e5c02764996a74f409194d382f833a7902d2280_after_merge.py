    async def user(
        self, ctx: commands.Context, user: str, number: int, delete_pinned: bool = False
    ):
        """Delete the last X messages from a specified user.

        Examples:
            `[p]cleanup user @\u200bTwentysix 2`
            `[p]cleanup user Red 6`
        """
        channel = ctx.channel

        member = None
        try:
            member = await commands.MemberConverter().convert(ctx, user)
        except commands.BadArgument:
            try:
                _id = int(user)
            except ValueError:
                raise commands.BadArgument()
        else:
            _id = member.id

        author = ctx.author

        if number > 100:
            cont = await self.check_100_plus(ctx, number)
            if not cont:
                return

        def check(m):
            if m.author.id == _id:
                return True
            elif m == ctx.message:
                return True
            else:
                return False

        to_delete = await self.get_messages_for_deletion(
            channel=channel,
            number=number,
            check=check,
            before=ctx.message,
            delete_pinned=delete_pinned,
        )
        reason = (
            "{}({}) deleted {} messages "
            " made by {}({}) in channel {}."
            "".format(author.name, author.id, len(to_delete), member or "???", _id, channel.name)
        )
        log.info(reason)

        await mass_purge(to_delete, channel)