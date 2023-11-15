    async def _cog_uninstall(self, ctx: commands.Context, *cogs: InstalledCog) -> None:
        """Uninstall cogs.

        You may only uninstall cogs which were previously installed
        by Downloader.
        """
        if not cogs:
            await ctx.send_help()
            return
        async with ctx.typing():
            uninstalled_cogs = []
            failed_cogs = []
            for cog in set(cogs):
                real_name = cog.name

                poss_installed_path = (await self.cog_install_path()) / real_name
                if poss_installed_path.exists():
                    with contextlib.suppress(commands.ExtensionNotLoaded):
                        ctx.bot.unload_extension(real_name)
                    await self._delete_cog(poss_installed_path)
                    uninstalled_cogs.append(inline(real_name))
                else:
                    failed_cogs.append(real_name)
            await self._remove_from_installed(cogs)

            message = ""
            if uninstalled_cogs:
                message += _("Successfully uninstalled cogs: ") + humanize_list(uninstalled_cogs)
            if failed_cogs:
                message += (
                    _("\nThese cog were installed but can no longer be located: ")
                    + humanize_list(tuple(map(inline, failed_cogs)))
                    + _(
                        "\nYou may need to remove their files manually if they are still usable."
                        " Also make sure you've unloaded those cogs with `{prefix}unload {cogs}`."
                    ).format(prefix=ctx.prefix, cogs=" ".join(failed_cogs))
                )
        await ctx.send(message)