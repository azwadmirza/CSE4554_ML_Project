    async def format_command_help(self, ctx: Context, obj: commands.Command):

        send = await ctx.bot._config.help.verify_exists()
        if not send:
            async for _ in self.help_filter_func(ctx, (obj,), bypass_hidden=True):
                # This is a really lazy option for not
                # creating a separate single case version.
                # It is efficient though
                #
                # We do still want to bypass the hidden requirement on
                # a specific command explicitly invoked here.
                send = True

        if not send:
            return

        command = obj

        description = command.description or ""
        tagline = (await ctx.bot._config.help.tagline()) or self.get_default_tagline(ctx)
        signature = f"`Syntax: {ctx.clean_prefix}{command.qualified_name} {command.signature}`"
        subcommands = None

        if hasattr(command, "all_commands"):
            grp = cast(commands.Group, command)
            subcommands = await self.get_group_help_mapping(ctx, grp)

        if await ctx.embed_requested():
            emb = {"embed": {"title": "", "description": ""}, "footer": {"text": ""}, "fields": []}

            if description:
                emb["embed"]["title"] = f"*{description[:2044]}*"

            emb["footer"]["text"] = tagline
            emb["embed"]["description"] = signature

            if command.help:
                splitted = command.help.split("\n\n")
                name = splitted[0]
                value = "\n\n".join(splitted[1:]).replace("[p]", ctx.clean_prefix)
                if not value:
                    value = EMPTY_STRING
                field = EmbedField(name[:252], value[:1024], False)
                emb["fields"].append(field)

            if subcommands:

                def shorten_line(a_line: str) -> str:
                    if len(a_line) < 70:  # embed max width needs to be lower
                        return a_line
                    return a_line[:67] + "..."

                subtext = "\n".join(
                    shorten_line(f"**{name}** {command.short_doc}")
                    for name, command in sorted(subcommands.items())
                )
                for i, page in enumerate(pagify(subtext, page_length=1000, shorten_by=0)):
                    if i == 0:
                        title = "**__Subcommands:__**"
                    else:
                        title = "**__Subcommands:__** (continued)"
                    field = EmbedField(title, page, False)
                    emb["fields"].append(field)

            await self.make_and_send_embeds(ctx, emb)

        else:  # Code blocks:

            subtext = None
            subtext_header = None
            if subcommands:
                subtext_header = "Subcommands:"
                max_width = max(discord.utils._string_width(name) for name in subcommands.keys())

                def width_maker(cmds):
                    doc_max_width = 80 - max_width
                    for nm, com in sorted(cmds):
                        width_gap = discord.utils._string_width(nm) - len(nm)
                        doc = com.short_doc
                        if len(doc) > doc_max_width:
                            doc = doc[: doc_max_width - 3] + "..."
                        yield nm, doc, max_width - width_gap

                subtext = "\n".join(
                    f"  {name:<{width}} {doc}"
                    for name, doc, width in width_maker(subcommands.items())
                )

            to_page = "\n\n".join(
                filter(
                    None,
                    (
                        description,
                        signature[1:-1],
                        command.help.replace("[p]", ctx.clean_prefix),
                        subtext_header,
                        subtext,
                    ),
                )
            )
            pages = [box(p) for p in pagify(to_page)]
            await self.send_pages(ctx, pages, embed=False)