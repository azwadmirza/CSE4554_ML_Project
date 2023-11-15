    async def reload_(self, ctx, *, cog_name: str):
        """Reloads packages"""

        cog_names = [c.strip() for c in cog_name.split(" ")]

        loaded, failed, not_found = await self._reload(cog_names)

        if loaded:
            fmt = "Package{plural} {packs} {other} reloaded."
            formed = self._get_package_strings(loaded, fmt, ("was", "were"))
            await ctx.send(formed)

        if failed:
            fmt = "Failed to reload package{plural} {packs}. Check your " "logs for details"
            formed = self._get_package_strings(failed, fmt)
            await ctx.send(formed)

        if not_found:
            fmt = "The package{plural} {packs} {other} not found in any cog path."
            formed = self._get_package_strings(not_found, fmt, ("was", "were"))
            await ctx.send(formed)