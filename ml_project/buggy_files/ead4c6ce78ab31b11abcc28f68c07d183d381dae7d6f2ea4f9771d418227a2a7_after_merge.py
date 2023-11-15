    async def delete_repo(self, name: str):
        """Delete a repository and its folders.

        Parameters
        ----------
        name : str
            The name of the repository to delete.

        Raises
        ------
        .MissingGitRepo
            If the repo does not exist.

        """
        repo = self.get_repo(name)
        if repo is None:
            raise errors.MissingGitRepo("There is no repo with the name {}".format(name))

        safe_delete(repo.folder_path)

        try:
            del self._repos[name]
        except KeyError:
            pass