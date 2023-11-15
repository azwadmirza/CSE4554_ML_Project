    async def add_repo(self, url: str, name: str, branch: str="master") -> Repo:
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
        name = self.validate_and_normalize_repo_name(name)
        if self.does_repo_exist(name):
            raise InvalidRepoName(
                "That repo name you provided already exists."
                " Please choose another."
            )

        # noinspection PyTypeChecker
        r = Repo(url=url, name=name, branch=branch,
                 folder_path=self.repos_folder / name)
        await r.clone()

        self._repos[name] = r

        return r