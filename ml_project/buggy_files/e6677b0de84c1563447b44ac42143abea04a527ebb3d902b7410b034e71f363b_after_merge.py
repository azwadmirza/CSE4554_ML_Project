async def help(ctx: commands.Context, *, command_name: str = ""):
    """Show help documentation.

    - `[p]help`: Show the help manual.
    - `[p]help command`: Show help for a command.
    - `[p]help Category`: Show commands and description for a category,
    """
    bot = ctx.bot
    if bot.pm_help:
        destination = ctx.author
    else:
        destination = ctx.channel

    use_embeds = await ctx.embed_requested()
    if use_embeds:
        formatter = bot.formatter
    else:
        formatter = dpy_formatter.HelpFormatter()

    if not command_name:
        # help by itself just lists our own commands.
        pages = await formatter.format_help_for(ctx, bot)
    else:
        command: commands.Command = bot.get_command(command_name)
        if command is None:
            if hasattr(formatter, "format_command_not_found"):
                msg = await formatter.format_command_not_found(ctx, command_name)
            else:
                msg = await default_command_not_found(ctx, command_name, use_embeds=use_embeds)
            pages = [msg]
        else:
            pages = await formatter.format_help_for(ctx, command)

    max_pages_in_guild = await ctx.bot.db.help.max_pages_in_guild()
    if len(pages) > max_pages_in_guild:
        destination = ctx.author
    if ctx.guild and not ctx.guild.me.permissions_in(ctx.channel).send_messages:
        destination = ctx.author
    try:
        for page in pages:
            if isinstance(page, discord.Embed):
                await destination.send(embed=page)
            else:
                await destination.send(page)
    except discord.Forbidden:
        await ctx.channel.send(
            _(
                "I couldn't send the help message to you in DM. Either you blocked me or you "
                "disabled DMs in this server."
            )
        )