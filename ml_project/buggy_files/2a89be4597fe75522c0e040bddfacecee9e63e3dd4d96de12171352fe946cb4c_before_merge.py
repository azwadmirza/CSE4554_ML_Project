    async def default_enable(self, cog_name: str):
        """
        Sets the default for a cog as enabled.

        Parameters
        ----------
        cog_name: str
            This should be the cog's qualified name, not necessarily the classname
        """
        await self._config.custom("COG_DISABLE_SETTINGS", cog_name, 0).disabled.clear()
        del self._disable_map[cog_name]