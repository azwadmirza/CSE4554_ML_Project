    async def cc_create_random(self, ctx: commands.Context, command: str.lower):
        """Create a CC where it will randomly choose a response!

        Note: This command is interactive.
        """
        if command in (*self.bot.all_commands, *commands.RESERVED_COMMAND_NAMES):
            await ctx.send(_("There already exists a bot command with the same name."))
            return
        responses = await self.commandobj.get_responses(ctx=ctx)
        if not responses:
            await ctx.send(_("Custom command process cancelled."))
            return
        try:
            await self.commandobj.create(ctx=ctx, command=command, response=responses)
            await ctx.send(_("Custom command successfully added."))
        except AlreadyExists:
            await ctx.send(
                _("This command already exists. Use `{command}` to edit it.").format(
                    command="{}customcom edit".format(ctx.prefix)
                )
            )