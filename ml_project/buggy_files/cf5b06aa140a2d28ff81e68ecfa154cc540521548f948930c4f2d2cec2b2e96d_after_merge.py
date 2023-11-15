    async def remove_path(self, path: Union[Path, str]) -> None:
        """Remove a path from the current paths list.

        Parameters
        ----------
        path : `pathlib.Path` or `str`
            Path to remove.

        """
        path = self._ensure_path_obj(path)
        paths = await self.user_defined_paths()

        paths.remove(path)
        await self.set_paths(paths)