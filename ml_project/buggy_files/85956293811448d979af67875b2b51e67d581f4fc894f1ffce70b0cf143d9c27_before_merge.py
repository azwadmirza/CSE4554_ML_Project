async def fuzzy_command_search(ctx: commands.Context, term: str):
    out = []

    if ctx.guild is not None:
        enabled = await ctx.bot.db.guild(ctx.guild).fuzzy()
    else:
        enabled = await ctx.bot.db.fuzzy()

    if not enabled:
        return None

    alias_cog = ctx.bot.get_cog("Alias")
    if alias_cog is not None:
        is_alias, alias = await alias_cog.is_alias(ctx.guild, term)

        if is_alias:
            return None

    customcom_cog = ctx.bot.get_cog("CustomCommands")
    if customcom_cog is not None:
        cmd_obj = customcom_cog.commandobj

        try:
            ccinfo = await cmd_obj.get(ctx.message, term)
        except:
            pass
        else:
            return None

    extracted_cmds = await filter_commands(
        ctx, process.extract(term, ctx.bot.walk_commands(), limit=5)
    )

    if not extracted_cmds:
        return None

    for pos, extracted in enumerate(extracted_cmds, 1):
        short = " - {}".format(extracted[0].short_doc) if extracted[0].short_doc else ""
        out.append("{0}. {1.prefix}{2.qualified_name}{3}".format(pos, ctx, extracted[0], short))

    return box("\n".join(out), lang="Perhaps you wanted one of these?")