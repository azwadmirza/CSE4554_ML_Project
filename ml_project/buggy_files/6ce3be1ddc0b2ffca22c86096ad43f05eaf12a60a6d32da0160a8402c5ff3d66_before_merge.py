    async def findcog(self, ctx: commands.Context, command_name: str):
        """Find which cog a command comes from.

        This will only work with loaded cogs.
        """
        command = ctx.bot.all_commands.get(command_name)

        if command is None:
            await ctx.send(_("That command doesn't seem to exist."))
            return

        # Check if in installed cogs
        cog_name = self.cog_name_from_instance(command.cog)
        installed, cog_installable = await self.is_installed(cog_name)
        if installed:
            msg = self.format_findcog_info(command_name, cog_installable)
        else:
            # Assume it's in a base cog
            msg = self.format_findcog_info(command_name, command.cog)

        await ctx.send(box(msg))