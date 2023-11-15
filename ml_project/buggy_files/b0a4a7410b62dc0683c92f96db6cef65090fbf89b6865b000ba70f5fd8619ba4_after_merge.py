    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return False
        if await ctx.bot.is_mod(member=ctx.author):
            return True

        room_id = await _config.guild(ctx.guild).room_lock()
        if room_id is None or ctx.channel.id == room_id:
            return True
        return False