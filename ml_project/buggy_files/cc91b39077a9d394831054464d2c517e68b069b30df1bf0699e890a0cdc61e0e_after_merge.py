    async def _repo_add(self, ctx, name: str, repo_url: str, branch: str = None):
        """Add a new repo.

        Repo names can only contain characters A-z, numbers, underscores, and hyphens.
        The branch will be the default branch if not specified.
        """
        agreed = await do_install_agreement(ctx)
        if not agreed:
            return
        if re.match("^[a-zA-Z0-9_\-]*$", name) is None:
            await ctx.send(
                _("Repo names can only contain characters A-z, numbers, underscores, and hyphens.")
            )
            return
        try:
            # noinspection PyTypeChecker
            repo = await self._repo_manager.add_repo(name=name, url=repo_url, branch=branch)
        except errors.ExistingGitRepo:
            await ctx.send(_("That git repo has already been added under another name."))
        except errors.CloningError as err:
            await ctx.send(_("Something went wrong during the cloning process."))
            log.exception(
                "Something went wrong whilst cloning %s (to revision: %s)",
                repo_url,
                branch,
                exc_info=err,
            )
        except OSError:
            await ctx.send(
                _(
                    "Something went wrong trying to add that repo. Your repo name might have an invalid character."
                )
            )
        else:
            await ctx.send(_("Repo `{name}` successfully added.").format(name=name))
            if repo.install_msg is not None:
                await ctx.send(repo.install_msg.replace("[p]", ctx.prefix))