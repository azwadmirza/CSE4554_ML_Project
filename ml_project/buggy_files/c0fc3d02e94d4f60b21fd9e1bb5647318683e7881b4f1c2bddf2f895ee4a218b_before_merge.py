    async def format(self) -> dict:
        """Formats command for output.

        Returns a dict used to build embed"""
        emb = {"embed": {"title": "", "description": ""}, "footer": {"text": ""}, "fields": []}

        if self.is_cog():
            translator = getattr(self.command, "__translator__", lambda s: s)
            description = (
                inspect.cleandoc(translator(self.command.__doc__))
                if self.command.__doc__
                else EMPTY_STRING
            )
        else:
            description = self.command.description

        if not description == "" and description is not None:
            description = "*{0}*".format(description)

        if description:
            # <description> portion
            emb["embed"]["description"] = description[:2046]

        tagline = await self.context.bot.db.help.tagline()
        if tagline:
            footer = tagline
        else:
            footer = self.get_ending_note()
        emb["footer"]["text"] = footer

        if isinstance(self.command, discord.ext.commands.core.Command):
            # <signature portion>
            emb["embed"]["title"] = emb["embed"]["description"]
            emb["embed"]["description"] = "`Syntax: {0}`".format(self.get_command_signature())

            # <long doc> section
            if self.command.help:
                splitted = self.command.help.split("\n\n")
                name = "__{0}__".format(splitted[0])
                value = "\n\n".join(splitted[1:]).replace("[p]", self.clean_prefix)
                if value == "":
                    value = EMPTY_STRING
                field = EmbedField(name[:252], value[:1024], False)
                emb["fields"].append(field)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                return emb

        def category(tup):
            # Turn get cog (Category) name from cog/list tuples
            cog = tup[1].cog_name
            return "**__{0}:__**".format(cog) if cog is not None else "**__\u200bNo Category:__**"

        # Get subcommands for bot or category
        filtered = await self.filter_command_list()

        if self.is_bot():
            # Get list of non-hidden commands for bot.
            data = sorted(filtered, key=category)
            for category, commands_ in itertools.groupby(data, key=category):
                commands_ = sorted(commands_)
                if len(commands_) > 0:
                    for i, page in enumerate(
                        pagify(self._add_subcommands(commands_), page_length=1000)
                    ):
                        title = category if i < 1 else f"{category} (continued)"
                        field = EmbedField(title, page, False)
                        emb["fields"].append(field)

        else:
            # Get list of commands for category
            filtered = sorted(filtered)
            if filtered:
                for i, page in enumerate(
                    pagify(self._add_subcommands(filtered), page_length=1000)
                ):
                    title = (
                        "**__Commands:__**"
                        if not self.is_bot() and self.is_cog()
                        else "**__Subcommands:__**"
                    )
                    if i > 0:
                        title += " (continued)"
                    field = EmbedField(title, page, False)
                    emb["fields"].append(field)

        return emb