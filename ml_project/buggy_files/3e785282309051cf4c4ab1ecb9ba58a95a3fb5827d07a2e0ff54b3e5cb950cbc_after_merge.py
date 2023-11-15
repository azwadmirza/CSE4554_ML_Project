    async def default_disable(self, cog_name: str):
        """
        Sets the default for a cog as disabled.

        Parameters
        ----------
        cog_name: str
            This should be the cog's qualified name, not necessarily the classname
        """
        await self._config.custom("COG_DISABLE_SETTINGS", cog_name, 0).disabled.set(True)
        self._disable_map.pop(cog_name, None)