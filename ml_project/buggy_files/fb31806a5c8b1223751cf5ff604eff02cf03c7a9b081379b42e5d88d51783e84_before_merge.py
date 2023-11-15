    async def _load_repos(self, set=False) -> MutableMapping[str, Repo]:
        ret = {}
        self.repos_folder.mkdir(parents=True, exist_ok=True)
        for folder in self.repos_folder.iterdir():
            if not folder.is_dir():
                continue
            try:
                ret[folder.stem] = await Repo.from_folder(folder)
            except RuntimeError:
                # Thrown when there's no findable git remote URL
                pass

        if set:
            self._repos = ret
        return ret