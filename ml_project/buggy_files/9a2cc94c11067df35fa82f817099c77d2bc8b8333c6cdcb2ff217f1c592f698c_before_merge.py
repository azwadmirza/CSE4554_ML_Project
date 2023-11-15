    async def install_cog(self, cog: Installable, target_dir: Path) -> bool:
        """Install a cog to the target directory.

        Parameters
        ----------
        cog : Installable
            The package to install.
        target_dir : pathlib.Path
            The target directory for the cog installation.

        Returns
        -------
        bool
            The success of the installation.

        """
        if cog not in self.available_cogs:
            raise DownloaderException("That cog does not exist in this repo")

        if not target_dir.is_dir():
            raise ValueError("That target directory is not actually a directory.")

        if not target_dir.exists():
            raise ValueError("That target directory does not exist.")

        return await cog.copy_to(target_dir=target_dir)