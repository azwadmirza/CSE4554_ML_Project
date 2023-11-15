    async def subcommand_not_found(self, ctx, command, not_found):
        """
        Sends an error
        """
        ret = T_("Command *{command_name}* has no subcommands.").format(
            command_name=command.qualified_name
        )
        await ctx.send(ret)