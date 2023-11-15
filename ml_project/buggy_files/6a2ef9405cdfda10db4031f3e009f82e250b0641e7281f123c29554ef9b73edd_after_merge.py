    async def get_last_module_occurrence(
        self, module_name: str, descendant_rev: Optional[str] = None
    ) -> Optional[Installable]:
        """
        Gets module's `Installable` from last commit in which it still occurs.

        Parameters
        ----------
        module_name : str
            Name of module to get.
        descendant_rev : `str`, optional
            Revision from which the module's commit must be
            reachable (i.e. descendant commit),
            defaults to repo's branch if not given.

        Returns
        -------
        `Installable`
            Module from last commit in which it still occurs
            or `None` if it couldn't be found.

        """
        if descendant_rev is None:
            descendant_rev = self.branch
        p = await self._run(
            ProcessFormatter().format(
                self.GIT_CHECK_IF_MODULE_EXISTS,
                path=self.folder_path,
                rev=descendant_rev,
                module_name=module_name,
            ),
            debug_only=True,
        )
        if p.returncode == 0:
            async with self.checkout(descendant_rev):
                return discord.utils.get(self.available_modules, name=module_name)

        git_command = ProcessFormatter().format(
            self.GIT_GET_LAST_MODULE_OCCURRENCE_COMMIT,
            path=self.folder_path,
            descendant_rev=descendant_rev,
            module_name=module_name,
        )
        p = await self._run(git_command)

        if p.returncode != 0:
            raise errors.GitException(
                f"Git log failed for repo at path: {self.folder_path}", git_command
            )

        commit = p.stdout.decode(**DECODE_PARAMS).strip()
        if commit:
            async with self.checkout(f"{commit}~"):
                return discord.utils.get(self.available_modules, name=module_name)
        return None