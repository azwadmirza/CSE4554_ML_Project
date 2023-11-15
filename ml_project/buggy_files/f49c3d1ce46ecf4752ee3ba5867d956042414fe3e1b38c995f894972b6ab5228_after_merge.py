async def create_and_invoke_context(
    realctx: commands.Context, command_str: str, user: discord.Member
):
    m = copy(realctx.message)
    m.content = command_str.format(user=user.mention, prefix=realctx.prefix)
    fctx = await realctx.bot.get_context(m, cls=commands.Context)
    try:
        await realctx.bot.invoke(fctx)
    except (commands.CheckFailure, commands.CommandOnCooldown):
        # reinvoke bypasses checks and we don't want to run bot owner only commands here
        if fctx.command.requires.privilege_level < PrivilegeLevel.BOT_OWNER:
            await fctx.reinvoke()