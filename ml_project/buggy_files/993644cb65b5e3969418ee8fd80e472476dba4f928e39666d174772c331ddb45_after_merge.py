    def _add_subcommands(self, cmds):
        entries = ""
        for name, command in cmds:
            if name in command.aliases:
                # skip aliases
                continue

            if self.is_cog() or self.is_bot():
                name = "{0}{1}".format(self.context.clean_prefix, name)

            entries += "**{0}**   {1}\n".format(name, command.short_doc)
        return entries