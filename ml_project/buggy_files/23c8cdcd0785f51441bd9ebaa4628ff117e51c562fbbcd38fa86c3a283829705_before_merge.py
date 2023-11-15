    async def add_repo(self, url: str, name: str, branch: Optional[str] = None) -> Repo:
        """Add and clone a git repository.

        Parameters
        ----------
        url : str
            URL to the git repository.
        name : str
            Internal name of the repository.
        branch : str
            Name of the default branch to checkout into.

        Returns
        -------
        Repo
            New Repo object representing the cloned repository.

        """
        if self.does_repo_exist(name):
            raise ExistingGitRepo(
                "That repo name you provided already exists. Please choose another."
            )

        url, branch = self._parse_url(url, branch)

        # noinspection PyTypeChecker
        r = Repo(url=url, name=name, branch=branch, folder_path=self.repos_folder / name)
        await r.clone()

        self._repos[name] = r

        return r