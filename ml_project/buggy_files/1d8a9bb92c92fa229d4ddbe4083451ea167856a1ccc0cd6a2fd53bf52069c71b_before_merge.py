    async def format_bot_help(self, ctx: Context):

        coms = await self.get_bot_help_mapping(ctx)
        if not coms:
            return

        description = ctx.bot.description or ""
        tagline = (await ctx.bot.db.help.tagline()) or self.get_default_tagline(ctx)

        if await ctx.embed_requested():

            emb = {"embed": {"title": "", "description": ""}, "footer": {"text": ""}, "fields": []}

            emb["footer"]["text"] = tagline
            if description:
                emb["embed"]["title"] = f"*{description[:2044]}*"

            for cog_name, data in coms:

                if cog_name:
                    title = f"**__{cog_name}:__**"
                else:
                    title = f"**__No Category:__**"

                cog_text = "\n".join(
                    f"**{name}** {command.short_doc}" for name, command in sorted(data.items())
                )

                for i, page in enumerate(pagify(cog_text, page_length=1000, shorten_by=0)):
                    title = title if i < 1 else f"{title} (continued)"
                    field = EmbedField(title, page, False)
                    emb["fields"].append(field)

            await self.make_and_send_embeds(ctx, emb)

        else:
            to_join = []
            if description:
                to_join.append(f"{description}\n")

            names = []
            for k, v in coms:
                names.extend(list(v.name for v in v.values()))

            max_width = max(
                discord.utils._string_width((name or "No Category:")) for name in names
            )

            def width_maker(cmds):
                doc_max_width = 80 - max_width
                for nm, com in cmds:
                    width_gap = discord.utils._string_width(nm) - len(nm)
                    doc = com.short_doc
                    if len(doc) > doc_max_width:
                        doc = doc[: doc_max_width - 3] + "..."
                    yield nm, doc, max_width - width_gap

            for cog_name, data in coms:

                title = f"{cog_name}:" if cog_name else "No Category:"
                to_join.append(title)

                for name, doc, width in width_maker(sorted(data.items())):
                    to_join.append(f"  {name:<{width}} {doc}")

            to_join.append(f"\n{tagline}")
            to_page = "\n".join(to_join)
            pages = [box(p) for p in pagify(to_page)]
            await self.send_pages(ctx, pages, embed=False)