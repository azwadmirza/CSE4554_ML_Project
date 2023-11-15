    async def send_help(self, ctx: Context, help_for: HelpTarget = None):
        """ 
        This delegates to other functions. 
        
        For most cases, you should use this and only this directly.
        """
        if help_for is None or isinstance(help_for, dpy_commands.bot.BotBase):
            await self.format_bot_help(ctx)
            return

        if isinstance(help_for, str):
            try:
                help_for = self.parse_command(ctx, help_for)
            except NoCommand:
                await self.command_not_found(ctx, help_for)
                return
            except NoSubCommand as exc:
                if self.CONFIRM_UNAVAILABLE_COMMAND_EXISTENCES:
                    await self.subcommand_not_found(ctx, exc.last, exc.not_found)
                    return
                help_for = exc.last

        if isinstance(help_for, commands.Cog):
            await self.format_cog_help(ctx, help_for)
        else:
            await self.format_command_help(ctx, help_for)