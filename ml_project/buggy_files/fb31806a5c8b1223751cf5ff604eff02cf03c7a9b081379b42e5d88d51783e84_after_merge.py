    async def _load_repos(self, set=False) -> MutableMapping[str, Repo]:
        ret = {}
        self.repos_folder.mkdir(parents=True, exist_ok=True)
        for folder in self.repos_folder.iterdir():
            if not folder.is_dir():
                continue
            try:
                ret[folder.stem] = await Repo.from_folder(folder)
            except errors.NoRemoteURL:
                log.warning("A remote URL does not exist for repo %s", folder.stem)
            except errors.DownloaderException as err:
                log.error("Discarding repo %s due to error.", folder.stem, exc_info=err)
                shutil.rmtree(
                    str(folder),
                    onerror=lambda func, path, exc: log.error(
                        "Failed to remove folder %s", path, exc_info=exc
                    ),
                )

        if set:
            self._repos = ret
        return ret