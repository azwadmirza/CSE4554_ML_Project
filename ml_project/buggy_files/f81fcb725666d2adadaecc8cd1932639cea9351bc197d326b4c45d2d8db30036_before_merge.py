    async def format_cog_help(self, ctx: Context, obj: commands.Cog):

        coms = await self.get_cog_help_mapping(ctx, obj)
        if not (coms or self.CONFIRM_UNAVAILABLE_COMMAND_EXISTENCES):
            return

        description = obj.help
        tagline = (await ctx.bot.db.help.tagline()) or self.get_default_tagline(ctx)

        if await ctx.embed_requested():
            emb = {"embed": {"title": "", "description": ""}, "footer": {"text": ""}, "fields": []}

            emb["footer"]["text"] = tagline
            if description:
                emb["embed"]["title"] = f"*{description[:2044]}*"

            if coms:
                command_text = "\n".join(
                    f"**{name}** {command.short_doc}" for name, command in sorted(coms.items())
                )
                for i, page in enumerate(pagify(command_text, page_length=1000, shorten_by=0)):
                    if i == 0:
                        title = "**__Commands:__**"
                    else:
                        title = "**__Commands:__** (continued)"
                    field = EmbedField(title, page, False)
                    emb["fields"].append(field)

            await self.make_and_send_embeds(ctx, emb)

        else:
            subtext = None
            subtext_header = None
            if coms:
                subtext_header = "Commands:"
                max_width = max(discord.utils._string_width(name) for name in coms.keys())

                def width_maker(cmds):
                    doc_max_width = 80 - max_width
                    for nm, com in sorted(cmds):
                        width_gap = discord.utils._string_width(nm) - len(nm)
                        doc = com.short_doc
                        if len(doc) > doc_max_width:
                            doc = doc[: doc_max_width - 3] + "..."
                        yield nm, doc, max_width - width_gap

                subtext = "\n".join(
                    f"  {name:<{width}} {doc}" for name, doc, width in width_maker(coms.items())
                )

            to_page = "\n\n".join(filter(None, (description, subtext_header, subtext)))
            pages = [box(p) for p in pagify(to_page)]
            await self.send_pages(ctx, pages, embed=False)