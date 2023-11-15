    async def _repo_add(self, ctx, name: RepoName, repo_url: str, branch: str=None):
        """
        Add a new repo to Downloader.

        Name can only contain characters A-z, numbers and underscore
        Branch will default to master if not specified
        """
        try:
            # noinspection PyTypeChecker
            await self._repo_manager.add_repo(
                name=name,
                url=repo_url,
                branch=branch
            )
        except ExistingGitRepo:
            await ctx.send(_("That git repo has already been added under another name."))
        except CloningError:
            await ctx.send(_("Something went wrong during the cloning process."))
            log.exception(_("Something went wrong during the cloning process."))
        else:
            await ctx.send(_("Repo `{}` successfully added.").format(name))