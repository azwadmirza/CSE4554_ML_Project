async def help(ctx, *cmds: str):
    """Shows help documentation.

    [p]**help**: Shows the help manual.
    [p]**help** command: Show help for a command
    [p]**help** Category: Show commands and description for a category"""
    destination = ctx.author if ctx.bot.pm_help else ctx

    def repl(obj):
        return _mentions_transforms.get(obj.group(0), "")

    use_embeds = await ctx.embed_requested()
    f = formatter.HelpFormatter()
    # help by itself just lists our own commands.
    if len(cmds) == 0:
        if use_embeds:
            embeds = await ctx.bot.formatter.format_help_for(ctx, ctx.bot)
        else:
            embeds = await f.format_help_for(ctx, ctx.bot)
    elif len(cmds) == 1:
        # try to see if it is a cog name
        name = _mention_pattern.sub(repl, cmds[0])
        command = None
        if name in ctx.bot.cogs:
            command = ctx.bot.cogs[name]
        else:
            command = ctx.bot.all_commands.get(name)
            if command is None:
                if use_embeds:
                    fuzzy_result = await fuzzy_command_search(ctx, name)
                    if fuzzy_result is not None:
                        await destination.send(
                            embed=await ctx.bot.formatter.cmd_not_found(
                                ctx, name, description=fuzzy_result
                            )
                        )
                else:
                    fuzzy_result = await fuzzy_command_search(ctx, name)
                    if fuzzy_result is not None:
                        await destination.send(
                            ctx.bot.command_not_found.format(name, fuzzy_result)
                        )
                return
        if use_embeds:
            embeds = await ctx.bot.formatter.format_help_for(ctx, command)
        else:
            embeds = await f.format_help_for(ctx, command)
    else:
        name = _mention_pattern.sub(repl, cmds[0])
        command = ctx.bot.all_commands.get(name)
        if command is None:
            if use_embeds:
                fuzzy_result = await fuzzy_command_search(ctx, name)
                if fuzzy_result is not None:
                    await destination.send(
                        embed=await ctx.bot.formatter.cmd_not_found(
                            ctx, name, description=fuzzy_result
                        )
                    )
            else:
                fuzzy_result = await fuzzy_command_search(ctx, name)
                if fuzzy_result is not None:
                    await destination.send(ctx.bot.command_not_found.format(name, fuzzy_result))
            return

        for key in cmds[1:]:
            try:
                key = _mention_pattern.sub(repl, key)
                command = command.all_commands.get(key)
                if command is None:
                    if use_embeds:
                        fuzzy_result = await fuzzy_command_search(ctx, name)
                        if fuzzy_result is not None:
                            await destination.send(
                                embed=await ctx.bot.formatter.cmd_not_found(
                                    ctx, name, description=fuzzy_result
                                )
                            )
                    else:
                        fuzzy_result = await fuzzy_command_search(ctx, name)
                        if fuzzy_result is not None:
                            await destination.send(
                                ctx.bot.command_not_found.format(name, fuzzy_result)
                            )
                    return
            except AttributeError:
                if use_embeds:
                    await destination.send(
                        embed=await ctx.bot.formatter.simple_embed(
                            ctx,
                            title='Command "{0.name}" has no subcommands.'.format(command),
                            color=await ctx.bot.formatter.color(),
                        )
                    )
                else:
                    await destination.send(ctx.bot.command_has_no_subcommands.format(command))
                return
        if use_embeds:
            embeds = await ctx.bot.formatter.format_help_for(ctx, command)
        else:
            embeds = await f.format_help_for(ctx, command)

    max_pages_in_guild = await ctx.bot.db.help.max_pages_in_guild()
    if len(embeds) > max_pages_in_guild:
        destination = ctx.author
    try:
        for embed in embeds:
            if use_embeds:
                try:
                    await destination.send(embed=embed)
                except discord.HTTPException:
                    destination = ctx.author
                    await destination.send(embed=embed)
            else:
                try:
                    await destination.send(embed)
                except discord.HTTPException:
                    destination = ctx.author
                    await destination.send(embed)
    except discord.Forbidden:
        await ctx.channel.send(
            "I couldn't send the help message to you in DM. Either you blocked me or you disabled DMs in this server."
        )