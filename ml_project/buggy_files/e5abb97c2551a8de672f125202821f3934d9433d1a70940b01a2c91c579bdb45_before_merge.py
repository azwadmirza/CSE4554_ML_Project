    async def cog_install_path(self):
        """Get the current cog install path.

        Returns
        -------
        pathlib.Path
            The default cog install path.

        """
        return await self.bot.cog_mgr.install_path()