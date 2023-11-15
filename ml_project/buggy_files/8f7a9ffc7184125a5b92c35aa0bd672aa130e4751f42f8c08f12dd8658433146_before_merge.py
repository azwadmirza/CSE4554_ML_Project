    async def _cog_update_logic(
        self,
        ctx: commands.Context,
        *,
        repo: Optional[Repo] = None,
        repos: Optional[List[Repo]] = None,
        rev: Optional[str] = None,
        cogs: Optional[List[InstalledModule]] = None,
    ) -> None:
        message = ""
        failed_repos = set()
        updates_available = set()

        async with ctx.typing():
            # this is enough to be sure that `rev` is not None (based on calls to this method)
            if repo is not None:
                rev = cast(str, rev)

                try:
                    await repo.update()
                except errors.UpdateError:
                    message = self.format_failed_repos([repo.name])
                    await ctx.send(message)
                    return

                try:
                    commit = await repo.get_full_sha1(rev)
                except errors.AmbiguousRevision as e:
                    msg = _(
                        "Error: short sha1 `{rev}` is ambiguous. Possible candidates:\n"
                    ).format(rev=rev)
                    for candidate in e.candidates:
                        msg += (
                            f"**{candidate.object_type} {candidate.rev}**"
                            f" - {candidate.description}\n"
                        )
                    for page in pagify(msg):
                        await ctx.send(msg)
                    return
                except errors.UnknownRevision:
                    message += _(
                        "Error: there is no revision `{rev}` in repo `{repo.name}`"
                    ).format(rev=rev, repo=repo)
                    await ctx.send(message)
                    return

                await repo.checkout(commit)
                cogs_to_check, __ = await self._get_cogs_to_check(
                    repos=[repo], cogs=cogs, update_repos=False
                )

            else:
                cogs_to_check, check_failed = await self._get_cogs_to_check(repos=repos, cogs=cogs)
                failed_repos.update(check_failed)

            pinned_cogs = {cog for cog in cogs_to_check if cog.pinned}
            cogs_to_check -= pinned_cogs
            if not cogs_to_check:
                message += _("There were no cogs to check.")
                if pinned_cogs:
                    cognames = [cog.name for cog in pinned_cogs]
                    message += _(
                        "\nThese cogs are pinned and therefore weren't checked: "
                    ) + humanize_list(tuple(map(inline, cognames)))
            else:
                cogs_to_update, libs_to_update = await self._available_updates(cogs_to_check)

                updates_available = cogs_to_update or libs_to_update
                cogs_to_update, filter_message = self._filter_incorrect_cogs(cogs_to_update)

                if updates_available:
                    updated_cognames, message = await self._update_cogs_and_libs(
                        cogs_to_update, libs_to_update
                    )
                else:
                    if repos:
                        message += _("Cogs from provided repos are already up to date.")
                    elif repo:
                        if cogs:
                            message += _(
                                "Provided cogs are already up to date with this revision."
                            )
                        else:
                            message += _(
                                "Cogs from provided repo are already up to date with this revision."
                            )
                    else:
                        if cogs:
                            message += _("Provided cogs are already up to date.")
                        else:
                            message += _("All installed cogs are already up to date.")
                if repo is not None:
                    await repo.checkout(repo.branch)
                if pinned_cogs:
                    cognames = [cog.name for cog in pinned_cogs]
                    message += _(
                        "\nThese cogs are pinned and therefore weren't checked: "
                    ) + humanize_list(tuple(map(inline, cognames)))
                message += filter_message

        if failed_repos:
            message += "\n" + self.format_failed_repos(failed_repos)

        repos_with_libs = {
            inline(module.repo.name)
            for module in cogs_to_update + libs_to_update
            if module.repo.available_libraries
        }
        if repos_with_libs:
            message += DEPRECATION_NOTICE.format(repo_list=humanize_list(list(repos_with_libs)))

        await ctx.send(message)

        if updates_available and updated_cognames:
            await self._ask_for_cog_reload(ctx, updated_cognames)